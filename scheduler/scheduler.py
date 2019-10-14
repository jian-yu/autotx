import json
import random
import threading
import time
from queue import Queue

import urllib3

from autotx import BROADCASTED_TX_DIR
from autotx.auth.auth import Auth
from autotx.bank.bank import Banker
from autotx.broadcast.broadcast import BroadCaster
from autotx.distribution.distribution import Distributor
from autotx.error.errors import (ERROR_BANKER, ERROR_BROADCASTER,
                                 ERROR_SCHEDULER, ERROR_SIGNER,
                                 ERROR_STAKINGER, ERROR_DISTRIBUTION, TxerError)
from autotx.log.logger import Logger
from autotx.module.moduletype import (TYPE_BANK, TYPE_BROADCAST, TYPE_SIGN,
                                      TYPE_STAKING, GetType, TYPE_DISTRIBUTION)
from autotx.module.registry import Registrar
from autotx.scheduler.args import (DelegateArgs, SendBroadcastArgs,
                                   SendCoinArgs, SendSignArgs, StakingArgs, WithdrawDelegatorOneRewardArgs, DistributionArgs)
from autotx.scheduler.base import Schedule
from autotx.scheduler.status import (SCHED_STATUS_INITIALIZED,
                                     SCHED_STATUS_INITIALIZING,
                                     SCHED_STATUS_STARTED,
                                     SCHED_STATUS_STARTING,
                                     SCHED_STATUS_STOPPED,
                                     SCHED_STATUS_STOPPING,
                                     SCHED_STATUS_UNINITIALIZED, CheckStatus)
from autotx.sign.sign import Signer
from autotx.staking.staking import Stakinger
from autotx.utils.contants import HTTP_METHOD_GET, LOG_TIME_FOEMAT
from autotx.utils.pool import Pool
from autotx.utils.rwlock import RWLock
from autotx.utils.timestamp import now_timestamp

http = urllib3.PoolManager()
TX_HASH_URL = 'http://172.38.8.89:1317/txs'


# Scheduler: main to schedule register modules
class Scheduler(Schedule):

    def __init__(self):
        self.__status = SCHED_STATUS_UNINITIALIZED
        self.__rwlock = RWLock()
        self.__registrar = None
        self.__bankerBufferPool = None
        self.__signBufferPool = None
        self.__broadcastBufferPool = None
        self.__stakingBufferPool = None
        self.__distributionBufferPool = None
        self.__errorBufferPool = None
        self.__auth = None
        self.__node = 'tcp://172.38.8.89:26657'

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
            self.staking(threading.currentThread())
            self.distribution(threading.currentThread())
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
            self.__stakingBufferPool.Close()
            self.__errorBufferPool.Close()
            self.__distributionBufferPool.Close()
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

    # register module
    def RegisterModules(self, modules):
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
            if broadcaster is None:
                continue
            ok, err = self.__registrar.Register(broadcaster)
            if err is not None:
                return err
            if ok is False:
                continue
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('broadcaster modules register successfully!'))
        for staking in modules.Stakings:
            if staking is None:
                continue
            ok, err = self.__registrar.Register(staking)
            if err is not None:
                return err
            if ok is False:
                continue
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('staking modules register successfully!'))
        for distributor in modules.Distributors:
            if distributor is None:
                continue
            ok, err = self.__registrar.Register(distributor)
            if err is not None:
                return err
            if ok is False:
                continue
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('distribution modules register successfully!'))

    def __initBufferPool(self, poolArgs):
        # init banker buffer pool
        if self.__bankerBufferPool is not None and self.__bankerBufferPool.Closed() is False:
            self.__bankerBufferPool.Close()
        self.__bankerBufferPool = Pool(poolArgs.BankerBufCap, poolArgs.BankerMaxBufNumber)
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('banker buffer pool built by bufCap = %s and maxBufNumber = %s' % (poolArgs.BankerBufCap, poolArgs.BankerMaxBufNumber)))
        # init signer buffer pool
        if self.__signBufferPool is not None and self.__signBufferPool.Closed() is False:
            self.__signBufferPool.Close()
        self.__signBufferPool = Pool(poolArgs.SignerBufCap, poolArgs.SignerBufMaxNumber)
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('signer buffer pool built by bufCap = %s and maxBufNumber = %s' % (poolArgs.SignerBufCap, poolArgs.SignerBufMaxNumber)))
        # init broadcaster buffer pool
        if self.__broadcastBufferPool is not None and self.__broadcastBufferPool.Closed() is False:
            self.__broadcastBufferPool.Close()
        self.__broadcastBufferPool = Pool(poolArgs.BroadcasterBufCap, poolArgs.BroadcasterMaxNumber)
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('broadcaster buffer pool built by bufCap = %s and maxBufNumber = %s' % (poolArgs.BroadcasterBufCap, poolArgs.BroadcasterMaxNumber)))
        # init staking buffer pool
        if self.__stakingBufferPool is not None and self.__stakingBufferPool.Closed() is False:
            self.__stakingBufferPool.Close()
        self.__stakingBufferPool = Pool(poolArgs.StakingBufCap, poolArgs.StakingMaxNumber)
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('staking buffer pool built by bufCap = %s and maxBufNumber = %s' % (poolArgs.StakingBufCap, poolArgs.StakingMaxNumber)))
        # init distribution buffer pool
        if self.__distributionBufferPool is not None and self.__distributionBufferPool.Closed() is False:
            self.__distributionBufferPool.Close()
        self.__distributionBufferPool = Pool(poolArgs.DistributionBufCap, poolArgs.DistributionMaxNumber)
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('distribution buffer pool built by bufCap = %s and maxBufNumber = %s' % (poolArgs.DistributionBufCap, poolArgs.DistributionMaxNumber)))
        # init error buffer pool
        if self.__errorBufferPool is not None and self.__errorBufferPool.Closed() is False:
            self.__errorBufferPool.Close()
        self.__errorBufferPool = Pool(poolArgs.BroadcasterBufCap, poolArgs.BroadcasterMaxNumber)
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('error buffer pool built by bufCap = %s and maxBufNumber = %s' % (poolArgs.ErrorBufCap, poolArgs.ErrorMaxNumber)))

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
        if self.__stakingBufferPool is None:
            return CheckBufferPoolError('empty staking buffer pool')
        if self.__stakingBufferPool is not None and self.__stakingBufferPool.Closed():
            self.__stakingBufferPool = Pool(self.__stakingBufferPool.BufCap, self.__stakingBufferPool.MaxBufNumber)
        if self.__distributionBufferPool is None:
            return CheckBufferPoolError('empty distribution buffer pool')
        if self.__distributionBufferPool is not None and self.__distributionBufferPool.Closed():
            self.__distributionBufferPool = Pool(self.__distributionBufferPool.BufCap, self.__distributionBufferPool.MaxBufNumber)

    def randomTx(self, schedulerThread):
        def func():
            while True:
                print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('current threading is %s' % (threading.currentThread())))
                print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('scheduler thread %s is alive' % (schedulerThread.getName())))
                accountList = list(self.__auth.GetAccountDict().values())
                validatorList = list(self.__auth.GetValidatorDict().values())
                self.randomWithdrawDelegatorOneRewardTx(accountList, validatorList)
                # if random.randint(0, 10) % 2 == 0:
                #     self.randomSendTx(accountList)
                # else:
                #     self.randomDelegateTx(accountList, validatorList)
                time.sleep(random.randint(1, 3))
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
            sendBank(data)
            return
        ok = isinstance(banker, Banker)
        if ok is False:
            errMsg = 'incorrect downloader type: ID: %s' % (banker.ID())
            sendError(TxerError(ERROR_BANKER, errMsg), banker.ID(), self.__errorBufferPool)
            sendBank(data)
            return
        sendedTxJsonFilePath, err = banker.SendCoins(data.srcAccount, data.dstAccount, data.coins, data.fees, data.gas, data.gasAdjust)
        if sendedTxJsonFilePath is not None:
            sendSignData = SendSignArgs(data.srcAccount, sendedTxJsonFilePath, self.__node)
            sendSign(sendSignData, self.__signBufferPool)
        if err is not None:
            sendError(err, banker.ID(), self.__errorBufferPool)

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

    def staking(self, schedulerThread):
        def func():
            while True:
                print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('current threading is %s' % (threading.currentThread())))
                print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('scheduler thread %s is alive' % (schedulerThread.getName())))
                stakingData, err = self.__stakingBufferPool.Get()
                if err is not None:
                    print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('the stakinger pool is closed, break'))
                    break
                # include delegate, redelegate and unbondingDelegate
                if stakingData and stakingData.getType() == 'delegate':
                    self.delegateOne(stakingData.getData())
        thread = threading.Thread(target=func)
        thread.name = 'staking'
        thread.start()

    def delegateOne(self, delegateData):
        if delegateData is None or isinstance(delegateData, DelegateArgs) is False or delegateData.Check() is not None:
            return
        stakinger, err = self.__registrar.Get(TYPE_STAKING)
        if stakinger is None or err is not None:
            errMsg = 'could not get a stakinger: %s' % (err)
            sendError(TxerError(ERROR_STAKINGER, errMsg), '', self.__errorBufferPool)
            stakingArgs = StakingArgs('delegate', delegateData)
            sendStaking(stakingArgs)
            return
        ok = isinstance(stakinger, Stakinger)
        if ok is False:
            errMsg = 'incorrect stakinger type: ID: %s' % (stakinger.ID())
            sendError(TxerError(ERROR_STAKINGER, errMsg), stakinger.ID(), self.__errorBufferPool)
            stakingArgs = StakingArgs('delegate', delegateData)
            sendStaking(stakingArgs)
            return
        delegateTxJsonFilePath, err = stakinger.Delegate(delegateData.delegator, delegateData.validator, delegateData.coin, delegateData.fees, delegateData.gas, delegateData.gasAdjust)
        if delegateTxJsonFilePath is not None:
            sendSignData = SendSignArgs(delegateData.delegator, delegateTxJsonFilePath, self.__node)
            sendSign(sendSignData, self.__signBufferPool)
        if err is not None:
            sendError(err, stakinger.ID(), self.__errorBufferPool)

    def distribution(self, schedulerThread):
        def func():
            while True:
                print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('current threading is %s' % (threading.currentThread())))
                print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('scheduler thread %s is alive' % (schedulerThread.getName())))
                distributionData, err = self.__distributionBufferPool.Get()
                if err is not None:
                    print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('the distribution pool is closed, break'))
                    break
                # include withdrawDelegatorOneReward, withdrawDelegatorAllReward
                if distributionData and distributionData.getType() == 'withdrawDelegatorOneReward':
                    self.withdrawDelegatorOneReward(distributionData.getData())
        thread = threading.Thread(target=func)
        thread.name = 'distribution'
        thread.start()

    def withdrawDelegatorOneReward(self, withdrawRewardData):
        if withdrawRewardData is None or isinstance(withdrawRewardData, WithdrawDelegatorOneRewardArgs) is False or withdrawRewardData.Check() is not None:
            return
        distributor, err = self.__registrar.Get(TYPE_DISTRIBUTION)
        if distributor is None or err is not None:
            errMsg = 'could not get a distributor: %s' % (err)
            sendError(TxerError(ERROR_DISTRIBUTION, errMsg), '', self.__errorBufferPool)
            distributionArgs = DistributionArgs('withdrawDelegatorOneReward', withdrawRewardData)
            sendDistribution(distributionArgs)
            return
        ok = isinstance(distributor, Distributor)
        if ok is False:
            errMsg = 'incorrect distributor type: ID: %s' % (distributor.ID())
            sendError(TxerError(ERROR_DISTRIBUTION, errMsg), distributor.ID(), self.__errorBufferPool)
            distributionArgs = DistributionArgs('withdrawDelegatorOneReward', withdrawRewardData)
            sendDistribution(distributionArgs)
            return
        distributionTxJsonFilePath, err = distributor.WithdrawDelegatorOneReward(withdrawRewardData.delegator, withdrawRewardData.validator, withdrawRewardData.fees, withdrawRewardData.gas, withdrawRewardData.gasAdjust)
        if distributionTxJsonFilePath is not None:
            sendSignData = SendSignArgs(withdrawRewardData.delegator, distributionTxJsonFilePath, self.__node)
            sendSign(sendSignData, self.__signBufferPool)
        if err is not None:
            print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn(err.msg))
            sendError(err, distributor.ID(), self.__errorBufferPool)

    def randomSendTx(self, accountList):
        length = len(accountList)
        if length == 0:
            return
        random0 = random.randint(0, length-1)
        random1 = random.randint(0, length-1)
        if random0 == random1:
            return
        srcAccount = accountList[random0]
        dstAccount = accountList[random1]
        if srcAccount is None:
            return
        if dstAccount is None:
            return
        sendCoins = [{'denom': 'hsn', 'amount': str(random.randint(0, 50000))}]
        fees = [{'denom': 'hsn', 'amount': str(random.randint(1, 10))}]
        gasList = ['100000', '200000', '150000']
        randomGas = random.randint(0, 2)
        gas = gasList[randomGas]
        gasAdjustList = ['1.0', '1.1', '1.2', '1.3', '1.4', '1.5']
        randomGasAdjust = random.randint(0, 5)
        gasAdjust = gasAdjustList[randomGasAdjust]
        sendCoinTx = SendCoinArgs(srcAccount, dstAccount, sendCoins, fees, gas, gasAdjust)
        sendBank(sendCoinTx, self.__bankerBufferPool)

    def randomDelegateTx(self, delegatorList, validatorList):
        length0 = len(delegatorList)
        length1 = len(validatorList)
        if length0 == 0 or length1 == 0:
            return
        random0 = random.randint(0, length0-1)
        random1 = random.randint(0, length1-1)
        delegator = delegatorList[random0]
        validator = validatorList[random1]
        if delegator is None:
            return
        if validator is None:
            return
        delegateCoin = {'denom': 'hsn', 'amount': str(random.randint(0, 1000))}
        fees = [{'denom': 'hsn', 'amount': str(random.randint(1, 10))}]
        gasList = ['100000', '200000', '150000']
        randomGas = random.randint(0, 2)
        gas = gasList[randomGas]
        gasAdjustList = ['1.0', '1.1', '1.2', '1.3', '1.4', '1.5']
        randomGasAdjust = random.randint(0, 5)
        gasAdjust = gasAdjustList[randomGasAdjust]
        delegateTx = DelegateArgs(delegator, validator, delegateCoin, fees, gas, gasAdjust)
        stakingArgs = StakingArgs('delegate', delegateTx)
        sendStaking(stakingArgs, self.__stakingBufferPool)

    def randomWithdrawDelegatorOneRewardTx(self, delegatorList, validatorList):
        length0 = len(delegatorList)
        length1 = len(validatorList)
        if length0 == 0 or length1 == 0:
            return
        random0 = random.randint(0, length0-1)
        random1 = random.randint(0, length1-1)
        delegator = delegatorList[random0]
        validator = validatorList[random1]
        if delegator is None:
            return
        if validator is None:
            return
        fees = [{'denom': 'hsn', 'amount': str(random.randint(1, 10))}]
        gasList = ['100000', '200000', '150000']
        randomGas = random.randint(0, 2)
        gas = gasList[randomGas]
        gasAdjustList = ['1.0', '1.1', '1.2', '1.3', '1.4', '1.5']
        randomGasAdjust = random.randint(0, 5)
        gasAdjust = gasAdjustList[randomGasAdjust]
        withdrawDelegatorOneRewardArgs = WithdrawDelegatorOneRewardArgs(delegator, validator, fees, gas, gasAdjust)
        distributionArgs = DistributionArgs('withdrawDelegatorOneReward', withdrawDelegatorOneRewardArgs)
        sendDistribution(distributionArgs, self.__distributionBufferPool)


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
                    print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('checkTx recycle : %s' % (err.msg)))
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


def sendBank(data, bankerBufferPool):
    if data is None or bankerBufferPool is None or bankerBufferPool.Closed():
        return False
    print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('enter send t banker'))

    def func(data):
        err = bankerBufferPool.Put(data)
        if err is not None:
            print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('the bank pool was closed'))

    thread = threading.Thread(target=func(data))
    thread.start()


def sendStaking(body, stakingBufferPool):
    if body is None or stakingBufferPool is None or stakingBufferPool.Closed():
        return False

    def func(body):
        err = stakingBufferPool.Put(body)
        if err is not None:
            print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('the delegate pool was closed'))

    thread = threading.Thread(target=func(body))
    thread.start()


def sendDistribution(body, distributionBufferPool):
    if body is None or distributionBufferPool is None or distributionBufferPool.Closed():
        return False

    def func(body):
        err = distributionBufferPool.Put(body)
        if err is not None:
            print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('the distribution pool was closed'))

    thread = threading.Thread(target=func(body))
    thread.start()


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
            elif moduleType == TYPE_STAKING:
                errType = ERROR_STAKINGER
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
        self.msg = msg

    def __str__(self):
        return self.msg


class CheckBufferPoolError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class ParseError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class CheckTxError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
