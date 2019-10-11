import random
import threading
from queue import Queue
import time
import json

from hsnhub_tx import BROADCASTED_TX_DIR
from hsnhub_tx.auth.auth import Auth
from hsnhub_tx.bank.bank import Banker
from hsnhub_tx.broadcast.broadcast import BroadCaster
from hsnhub_tx.error.errors import (ERROR_BANKER, ERROR_BROADCASTER,
                                    ERROR_SCHEDULER, ERROR_SIGNER, TxerError)
from hsnhub_tx.log.logger import Logger
from hsnhub_tx.module.moduletype import (TYPE_BANK, TYPE_BROADCAST, TYPE_SIGN,
                                         GetType)
from hsnhub_tx.module.registry import Registrar
from hsnhub_tx.scheduler.args import (SendBroadcastArgs, SendCoinArgs,
                                      SendSignArgs)
from hsnhub_tx.scheduler.base import Schedule
from hsnhub_tx.scheduler.status import (SCHED_STATUS_INITIALIZED,
                                        SCHED_STATUS_INITIALIZING,
                                        SCHED_STATUS_STARTED,
                                        SCHED_STATUS_STARTING,
                                        SCHED_STATUS_UNINITIALIZED,
                                        SCHED_STATUS_STOPPED,
                                        SCHED_STATUS_STOPPING,
                                        CheckStatus)
from hsnhub_tx.sign.sign import Signer
from hsnhub_tx.utils.contants import LOG_TIME_FOEMAT
from hsnhub_tx.utils.pool import Pool
from hsnhub_tx.utils.rwlock import RWLock
from hsnhub_tx.utils.timestamp import now_timestamp
import urllib3
from hsnhub_tx.utils.contants import HTTP_METHOD_GET
http = urllib3.PoolManager()
TX_HASH_URL = 'http://172.38.8.89:1317/txs'


class Scheduler(Schedule):

    def __init__(self):
        self.__status = SCHED_STATUS_UNINITIALIZED
        self.__rwlock = RWLock()
        self.__registrar = None
        self.__bankerBufferPool = None
        self.__signBufferPool = None
        self.__broadcastBufferPool = None
        self.__errorBufferPool = None
        self.__auth = None
        self.__node = 'tcp://172.38.8.89:26657'

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def Init(self, modulesArgs, poolArgs, node):
        err = None
        srcStatus = self.__status
        dstStatus = SCHED_STATUS_INITIALIZING
        try:
            print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('Initialized scheduler ...'))
            print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('check scheduler status...'))
            err = CheckStatus(srcStatus, dstStatus)
            if err is not None:
                return err
            self.SetStatus(dstStatus)
            err = modulesArgs.Check()
            if err is not None:
                return err
            print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('scheduler is being initialing...'))
            if self.__registrar is None:
                self.__registrar = Registrar()
            else:
                self.__registrar.Clear()
            self.__initBufferPool(poolArgs)
            err = self.RegisterModules(modulesArgs)
            if err is not None:
                return err
            if node is not None:
                self.__node = node
            print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('scheduler has been initialized'))
            return err
        finally:
            if err is not None:
                self.SetStatus(srcStatus)
            else:
                self.SetStatus(SCHED_STATUS_INITIALIZED)

    def Start(self, auth):
        err = None
        srcStatus = self.__status
        dstStatus = SCHED_STATUS_STARTING
        try:
            print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('Start scheduler ...'))
            print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('Check scheduler status...'))
            err = CheckStatus(srcStatus, dstStatus)
            if err is not None:
                return err
            self.SetStatus(dstStatus)
            print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('Check auth module...'))
            if isinstance(auth, Auth) is False:
                return err
            print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('Auth module is valid...'))
            self.__auth = auth
            err = self.__checkBufferPool()
            if err is not None:
                return err
            self.randomTx(threading.currentThread())
            self.transfer(threading.currentThread())
            self.sign(threading.currentThread())
            self.broadcast(threading.currentThread())
            print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('Scheduler has been started.'))
            return err
        finally:
            if err is not None:
                self.SetStatus(srcStatus)
            else:
                self.SetStatus(SCHED_STATUS_STARTED)

    def Stop(self):
        err = None
        srcStatus = self.__status
        dstStatus = SCHED_STATUS_STOPPING
        try:
            print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('Stop scheduler ...'))
            print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('Check scheduler status...'))
            err = CheckStatus(srcStatus, dstStatus)
            if err is not None:
                return err
            self.SetStatus(dstStatus)
            self.__bankerBufferPool.Close()
            self.__signBufferPool.Close()
            self.__broadcastBufferPool.Close()
            self.__errorBufferPool.Close()
            print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('Scheduler has been stopped.'))
            return err
        finally:
            if err is not None:
                self.SetStatus(srcStatus)
            else:
                self.SetStatus(SCHED_STATUS_STOPPED)

    def Status(self):
        self.__rwlock.acquire_read()
        try:
            return self.__status
        finally:
            self.__rwlock.release()

    def ErrorQueue(self, schedulerThread):
        errorBufPool = self.__errorBufferPool
        errorQueue = Queue(errorBufPool.BufCap)

        def func(errorBufPool, errorQueue):
            while True:
                print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('current threading is %s' % (threading.currentThread())))
                print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('scheduler thread %s is alive' % (schedulerThread.getName())))
                data, err = self.__errorBufferPool.Get()
                if err is not None:
                    print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('the error pool is closed, break'))
                    break
                errorQueue.put_nowait(data)
        thread = threading.Thread(target=func(errorBufPool, errorQueue))
        thread.start()
        return errorQueue

    def SetStatus(self, dstStatus):
        self.__rwlock.acquire_write()
        try:
            self.__status = dstStatus
        finally:
            self.__rwlock.release()

    # 组件注册
    def RegisterModules(self, modules):
        print(modules.Bankers)
        for banker in modules.Bankers:
            if banker is None:
                continue
            ok, err = self.__registrar.Register(banker)
            if err is not None:
                return err
            if ok is False:
                continue
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('banker modules register successfully!'))
        for signer in modules.Signers:
            if signer is None:
                continue
            ok, err = self.__registrar.Register(signer)
            if err is not None:
                return err
            if ok is False:
                continue
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('signer modules register successfully!'))
        for broadcaster in modules.Broadcasters:
            if signer is None:
                continue
            ok, err = self.__registrar.Register(broadcaster)
            if err is not None:
                return err
            if ok is False:
                continue
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('broadcaster modules register successfully!'))

    def __initBufferPool(self, poolArgs):
        # 初始化banker缓存池
        if self.__bankerBufferPool is not None and self.__bankerBufferPool.Closed() is False:
            self.__bankerBufferPool.Close()
        self.__bankerBufferPool = Pool(poolArgs.BankerBufCap, poolArgs.BankerMaxBufNumber)
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('banker buffer pool built by bufCap = %s and maxBufNumber = %s' % (poolArgs.BankerBufCap, poolArgs.BankerMaxBufNumber)))
        # 初始化signer缓存池
        if self.__signBufferPool is not None and self.__signBufferPool.Closed() is False:
            self.__signBufferPool.Close()
        self.__signBufferPool = Pool(poolArgs.SignerBufCap, poolArgs.SignerBufMaxNumber)
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('signer buffer pool built by bufCap = %s and maxBufNumber = %s' % (poolArgs.SignerBufCap, poolArgs.SignerBufMaxNumber)))
        # 初始化广播交易缓存池
        if self.__broadcastBufferPool is not None and self.__broadcastBufferPool.Closed() is False:
            self.__broadcastBufferPool.Close()
        self.__broadcastBufferPool = Pool(poolArgs.BroadcasterBufCap, poolArgs.BroadcasterMaxNumber)
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('broadcaster buffer pool built by bufCap = %s and maxBufNumber = %s' % (poolArgs.BroadcasterBufCap, poolArgs.BroadcasterMaxNumber)))
        # 初始化错误缓存池
        if self.__errorBufferPool is not None and self.__errorBufferPool.Closed() is False:
            self.__errorBufferPool.Close()
        self.__errorBufferPool = Pool(poolArgs.BroadcasterBufCap, poolArgs.BroadcasterMaxNumber)
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('error buffer pool built by bufCap = %s and maxBufNumber = %s' % (poolArgs.BroadcasterBufCap, poolArgs.BroadcasterMaxNumber)))

    def __checkBufferPool(self):
        if self.__bankerBufferPool is None:
            return CheckBufferPoolError('empty banker buffer pool')
        if self.__bankerBufferPool is not None and self.__bankerBufferPool.Closed():
            self.__bankerBufferPool = Pool(self.__bankerBufferPool.BufCap, self.__bankerBufferPool.MaxBufNumber)
        if self.__signBufferPool is None:
            return CheckBufferPoolError('empty sign buffer pool')
        if self.__signBufferPool is not None and self.__signBufferPool.Closed():
            self.__signBufferPool = Pool(self.__signBufferPool.BufCap, self.__signBufferPool.MaxBufNumber)
        if self.__broadcastBufferPool is None:
            return CheckBufferPoolError('empty broadcast buffer pool')
        if self.__broadcastBufferPool is not None and self.__broadcastBufferPool.Closed():
            self.__broadcastBufferPool = Pool(self.__broadcastBufferPool.BufCap, self.__broadcastBufferPool.MaxBufNumber)
        if self.__errorBufferPool is None:
            return CheckBufferPoolError('empty error buffer pool')
        if self.__errorBufferPool is not None and self.__errorBufferPool.Closed():
            self.__errorBufferPool = Pool(self.__errorBufferPool.BufCap, self.__errorBufferPool.MaxBufNumber)

    def randomTx(self, schedulerThread):
        def func():
            while True:
                print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('current threading is %s' % (threading.currentThread())))
                print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('scheduler thread %s is alive' % (schedulerThread.getName())))
                accountDict = self.__auth.GetAccountDict()
                accountList = list(accountDict.values())
                length = len(accountList)
                if length == 0:
                    continue
                random0 = random.randint(0, length-1)
                random1 = random.randint(0, length-1)
                if random0 == random1:
                    continue
                srcAccount = accountList[random0]
                dstAccount = accountList[random1]
                if srcAccount is None:
                    continue
                if dstAccount is None:
                    continue
                sendCoins = [{'denom': 'hsn', 'amount': str(random.randint(0, 50000))}]
                fees = [{'denom': 'hsn', 'amount': str(random.randint(0, 10))}]
                gasList = ['100000', '200000', '150000']
                randomGas = random.randint(0, 2)
                gas = gasList[randomGas]
                gasAdjustList = ['1.0', '1.1', '1.2', '1.3', '1.4', '1.5']
                randomGasAdjust = random.randint(0, 5)
                gasAdjust = gasAdjustList[randomGasAdjust]
                sendCoinTx = SendCoinArgs(srcAccount, dstAccount, sendCoins, fees, gas, gasAdjust)
                self.sendBank(sendCoinTx)
                # time.sleep(random.randint(0, 3600))
        thread = threading.Thread(target=func)
        thread.name = 'randomTx'
        thread.start()

    def transfer(self, schedulerThread):
        def func():
            while True:
                print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('current threading is %s' % (threading.currentThread())))
                print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('scheduler thread %s is alive' % (schedulerThread.getName())))
                data, err = self.__bankerBufferPool.Get()
                if err is not None:
                    print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('the banker pool is closed, break'))
                    break
                self.transferOne(data)
        thread = threading.Thread(target=func)
        thread.name = 'transfer'
        thread.start()

    def transferOne(self, data):
        if data is None or isinstance(data, SendCoinArgs) is False or data.Check() is not None:
            return
        banker, err = self.__registrar.Get(TYPE_BANK)
        if banker is None or err is not None:
            errMsg = 'could not get a banker: %s' % (err)
            sendError(TxerError(ERROR_BANKER, errMsg), '', self.__errorBufferPool)
            self.sendBank(data)
            return
        ok = isinstance(banker, Banker)
        if ok is False:
            errMsg = 'incorrect downloader type: ID: %s' % (banker.ID())
            sendError(TxerError(ERROR_BANKER, errMsg), banker.ID(), self.__errorBufferPool)
            self.sendBank(data)
            return
        sendedTxJsonFilePath, err = banker.SendCoins(data.srcAccount, data.dstAccount, data.coins, data.fees, data.gas, data.gasAdjust)
        if sendedTxJsonFilePath is not None:
            sendSignData = SendSignArgs(data.srcAccount, sendedTxJsonFilePath, self.__node)
            sendSign(sendSignData, self.__signBufferPool)
        if err is not None:
            sendError(err, banker.ID(), self.__errorBufferPool)

    def sendBank(self, data):
        if data is None or self.__bankerBufferPool is None or self.__bankerBufferPool.Closed():
            return False
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('enter send t banker'))

        def func(data):
            err = self.__bankerBufferPool.Put(data)
            if err is not None:
                print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('the bank pool was closed'))

        thread = threading.Thread(target=func(data))
        thread.start()

    def sign(self, schedulerThread):
        def func():
            while True:
                print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('current threading is %s' % (threading.currentThread())))
                print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('scheduler thread %s is alive' % (schedulerThread.getName())))
                data, err = self.__signBufferPool.Get()
                if err is not None:
                    print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('the sign pool is closed, break'))
                    break
                self.signOne(data)
        thread = threading.Thread(target=func)
        thread.name = 'sign'
        thread.start()

    def signOne(self, data):
        if data is None or isinstance(data, SendSignArgs) is False or data.Check() is not None:
            return
        signer, err = self.__registrar.Get(TYPE_SIGN)
        if signer is None or err is not None:
            errMsg = 'could not get a signer: %s' % (err)
            sendError(TxerError(ERROR_BANKER, errMsg), '', self.__errorBufferPool)
            sendSign(data, self.__signBufferPool)
            return
        ok = isinstance(signer, Signer)
        if ok is False:
            errMsg = 'incorrect downloader type: ID: %s' % (signer.ID())
            sendError(TxerError(ERROR_SIGNER, errMsg), signer.ID(), self.__errorBufferPool)
            sendSign(data, self.__signBufferPool)
            return
        signedData, err = signer.Sign(data.srcAccount, data.sendedJsonFilePath, data.node)
        if signedData is not None:
            sendBroadcastData = SendBroadcastArgs(data.srcAccount, signedData)  # mode 为默认
            sendBroadcast(sendBroadcastData, self.__broadcastBufferPool)
        if err is not None:
            sendError(err, signer.ID(), self.__errorBufferPool)

    def broadcast(self, schedulerThread):
        def func():
            while True:
                print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('current threading is %s' % (threading.currentThread())))
                print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('scheduler thread %s is alive' % (schedulerThread.getName())))
                broadcastData, err = self.__broadcastBufferPool.Get()
                if err is not None:
                    print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('the broadcast pool is closed, break'))
                    break
                self.broadcastOne(broadcastData)
        thread = threading.Thread(target=func)
        thread.name = 'broadcast'
        thread.start()

    def broadcastOne(self, broadcastData):
        if broadcastData is None or isinstance(broadcastData, SendBroadcastArgs) is False or broadcastData.Check() is not None:
            return
        broadcaster, err = self.__registrar.Get(TYPE_BROADCAST)
        if broadcaster is None or err is not None:
            errMsg = 'could not get a broadcaster: %s' % (err)
            sendError(TxerError(ERROR_BROADCASTER, errMsg), '', self.__errorBufferPool)
            sendBroadcast(broadcastData, self.__signBufferPool)
            return
        ok = isinstance(broadcaster, BroadCaster)
        if ok is False:
            errMsg = 'incorrect downloader type: ID: %s' % (broadcaster.ID())
            sendError(TxerError(ERROR_SIGNER, errMsg), broadcaster.ID(), self.__errorBufferPool)
            sendBroadcast(broadcastData, self.__signBufferPool)
            return
        broadcastedData, err = broadcaster.BroadCastTx(broadcastData.body, broadcastData.mode)
        if broadcastData is not None:
            saveTxRecord(broadcastData.srcAccount, broadcastedData)  # 保存交易记录
        if err is not None:
            sendError(err, broadcaster.ID(), self.__errorBufferPool)


def saveTxRecord(srcAccount, body):
    def func(srcAccount, body):
        delay = 1
        while True:
            time.sleep(delay)
            txResult, err = checkTx(body)
            if txResult is not None:
                with open(BROADCASTED_TX_DIR + '/' + srcAccount.getAddress() + '|' + str(now_timestamp()) + '.json', 'w', encoding='utf-8') as broadcastedTxFile:
                    if broadcastedTxFile.writable():
                        broadcastedTxFile.write(txResult)
                        return
            if err is not None:
                if delay == 6:
                    break
                else:
                    delay += 1
                    print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('checkTx recycle : %s' % (err.message)))
    thread = threading.Thread(target=func(srcAccount, body))
    thread.start()


def checkTx(body):
    tx = json.loads(body)
    if tx is None:
        return None, ParseError('checkTx: json.loads: json parse error')
    if tx.get('txhash') is None:
        return None, CheckTxError('checkTx: txhash is not found')
    try:
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('current tx hash is %s' % (tx['txhash'])))
        resp = http.request(HTTP_METHOD_GET, TX_HASH_URL + '/' + tx['txhash'])
        if resp and resp.status == 200:
            if tx.get('logs') is not None and tx['logs'][0].get('success') is not None and (tx['logs'][0])['success'] is True:
                return resp.data.decode('utf-8'), None
            else:
                return None, None
        elif resp and resp.status == 404:
            return None, CheckTxError('checkTx: txhash is invalid')
        elif resp and resp.status == 500:
            return None, CheckTxError('Internal Server Error')
        return None, CheckTxError('unknown error')
    except Exception as e:
        return None, CheckTxError(e)


def sendBroadcast(body, broadcastBufferPool):
    if body is None or broadcastBufferPool is None or broadcastBufferPool.Closed():
        return False

    def func(body):
        err = broadcastBufferPool.Put(body)
        if err is not None:
            print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('the broadcast pool was closed'))

    thread = threading.Thread(target=func(body))
    thread.start()


def sendSign(sendSignData, signBufferPool):
    if sendSignData is None or signBufferPool is None or signBufferPool.Closed():
        return False

    def func(sendSignData):
        err = signBufferPool.Put(sendSignData)
        if err is not None:
            print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('the sign pool was closed'))

    thread = threading.Thread(target=func(sendSignData))
    thread.start()


def sendError(err, mid, errBufPool):
    if err is None or errBufPool is None or errBufPool.Closed():
        return False
    ok = False
    txerError = None
    ok = isinstance(err, TxerError)
    if ok is False:
        errType = None
        moduleType, err = GetType(mid)
        if ok is not None:
            errType = ERROR_SCHEDULER
        else:
            if moduleType == TYPE_BANK:
                errType = ERROR_BANKER
            elif moduleType == TYPE_BROADCAST:
                errType = ERROR_BROADCASTER
            elif moduleType == TYPE_SIGN:
                errType = ERROR_SIGNER
        txerError = TxerError(errType, err)
    if errBufPool.Closed():
        return False

    def func(txerError):
        err = errBufPool.Put(txerError)
        if err is not None:
            print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('the error pool was closed'))

    thread = threading.Thread(target=func(txerError))
    thread.start()
    return True


class ModulesCheckError(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


class CheckBufferPoolError(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


class ParseError(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


class CheckTxError(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message
