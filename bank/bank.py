import json
import time

import urllib3

from autotx import HSN_CHAIN_ID, UNSIGN_JSON_DIR
from autotx.bank.base import Bank
from autotx.bank.req import GenSendTxJson
from autotx.common.baseReq import GenBaseReqJson
from autotx.module.module import Module
from autotx.utils.contants import HTTP_METHOD_GET, HTTP_METHOD_POST
from autotx.utils.timestamp import now_timestamp

http = urllib3.PoolManager()
ACCOUNT_BALANCE_URL = 'http://172.38.8.89:1317/bank/balances/%s'
SEND_TX_URL = 'http://172.38.8.89:1317/bank/accounts/%s/transfers'


class Banker(Module, Bank):

    def __init__(self, mid, calculateCost):
        super(Banker, self).__init__(mid, calculateCost)

    def GetBalance(self, account):
        self.IncrHandingCount()
        self.IncrCalledCount()
        now = now_timestamp()
        try:
            if account is None:
                return None, BankerError('account cannot be none')
            if account.getAddress() == '':
                return None, BankerError('account address cannot be empty')
            account, err = query(account)
            if err is not None:
                return None, BankerError(err)
            self.IncrCompletedCount()
            return account.getCoins(), None
        finally:
            self.SetCalculateCost(now_timestamp() - now)
            self.DecrHandingCount()

    def SendCoins(self, srcAccount, dstAccount, coins, fees, gas, gasAdjust):
        self.IncrHandingCount()
        self.IncrCalledCount()
        now = now_timestamp()
        try:
            if srcAccount is None or dstAccount is None or coins is None:
                return None, BankerError('args are invalid')
            if srcAccount.getAddress() == '' or dstAccount.getAddress() == '':
                return None, BankerError('account address cannot be empty')
            srcCoins, err = self.GetBalance(srcAccount)
            if err is not None:
                return None, BankerError(err.msg)
            for srcKey, srcVal in srcCoins.items():
                for coin in coins:
                    if srcKey == coin['denom']:
                        if int(srcVal) < int(coin['amount']):
                            return None, BankerError('src account balances are insufficient!')
            memo = '%s send %s to %s' % (srcAccount.getAddress(), coins, dstAccount.getAddress())
            baseReqJson, err = GenBaseReqJson(srcAccount.getAddress(), HSN_CHAIN_ID, str(srcAccount.getAccNum()), str(srcAccount.getSequence()), fees, False, memo, gas, gasAdjust)
            if err is not None:
                return None, err
            sendTxJson, err = GenSendTxJson(baseReqJson, coins)
            if err is not None:
                return None, err
            sendedTxJson, err = postSendTxJson(sendTxJson, dstAccount.getAddress())
            if err is not None:
                return None, err
            # 写入到文件中
            unSignJsonFileName = srcAccount.getAddress() + '|' + str(int(round(time.time() * 1000))) + '.json'
            unSignJsonPath = UNSIGN_JSON_DIR + '/' + unSignJsonFileName
            with open(unSignJsonPath, 'w', encoding='utf-8') as unSignJsonFile:
                if unSignJsonFile.writable():
                    unSignJsonFile.write(sendedTxJson)
                    self.IncrCompletedCount()
                    return unSignJsonPath, None
            return None, BankerError('unable to write into a file')
        finally:
            self.SetCalculateCost(now_timestamp() - now)
            self.DecrHandingCount()


def query(account):
    try:
        resp = http.request(HTTP_METHOD_GET, ACCOUNT_BALANCE_URL % (account.getAddress()))
        if resp and resp.status == 200:
            jsonData = json.loads(resp.data.decode('utf-8'))
            if jsonData and len(list(jsonData.get('result'))) == 0:
                return None, BankerError('account does not exit')
            else:
                coins = jsonData.get('result')
                account.setCoins(coins)
                return account, None
        if resp.status == 500:
            return None, BankerError('account address is invalid')
    except Exception as e:
        return None, BankerError(e)


def postSendTxJson(sendTxJson, dstAccAddr):
    try:
        resp = http.request(HTTP_METHOD_POST, SEND_TX_URL % (dstAccAddr), body=sendTxJson)
        if resp and resp.status == 200:
            return resp.data.decode('utf-8'), None
        elif resp and resp.status == 400:
            return None, BankerError('Invalid request')
        elif resp and resp.status == 500:
            return None, BankerError('Server internal error')
        else:
            return None, BankerError('Unknown error')
    except Exception as e:
        return None, BankerError(e)


class BankerError(Exception):

    def __init__(self, msg):
        self.__message = msg

    def __str__(self):
        return self.__message
