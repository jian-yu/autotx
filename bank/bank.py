import json
import time

import urllib3

from autotx import HSN_CHAIN_ID, UNSIGN_JSON_DIR
from autotx.bank.base import Bank
from autotx.utils.file import WriteToFile
from autotx.bank.req import GenSendTxJson
from autotx.common.baseReq import GenBaseReqJson
from autotx.module.module import Module
from autotx.utils.contants import HTTP_METHOD_GET, HTTP_METHOD_POST, ACCOUNT_BALANCE_URL, SEND_TX_URL, ACCOUNT_INFO_URL
from autotx.utils.timestamp import now_timestamp

http = urllib3.PoolManager()


class Banker(Module, Bank):

    def __init__(self, mid, calculateCost):
        super(Banker, self).__init__(mid, calculateCost)

    def SendCoins(self, srcAccount, dstAccount, coins, fees, gas, gasAdjust):
        self.IncrHandingCount()
        self.IncrCalledCount()
        now = now_timestamp()
        try:
            srcCoins, err = GetBalance(srcAccount)
            if err is not None:
                return None, BankerError(err.msg)
            for srcKey, srcVal in srcCoins.items():
                for coin in coins:
                    if srcKey == coin['denom']:
                        if int(srcVal) < int(coin['amount']):
                            return None, BankerError('src account balances are insufficient!')
            memo = '%s send %s to %s' % (srcAccount.getAddress(), json.dumps(coins), dstAccount.getAddress())
            srAccount = QueryAccountInfo(srcAccount)
            # 获取账户最新信息
            if srAccount is None:
                return None, BankerError('srcAccount is invalid!')
            baseReqJson, err = GenBaseReqJson(srcAccount, HSN_CHAIN_ID, fees, False, memo, gas, gasAdjust)
            if err is not None:
                return None, err
            sendTxJson, err = GenSendTxJson(baseReqJson, coins)
            if err is not None:
                return None, err
            sendedTxJson, err = postSendTxJson(sendTxJson, dstAccount.getAddress())
            if err is not None:
                return None, err
            # 写入到文件中
            unSignJsonFileName = '[sendCoins]--' + srcAccount.getAddress() + '|' + str(int(round(time.time() * 1000))) + '.json'
            unSignJsonPath, err = WriteToFile(UNSIGN_JSON_DIR, unSignJsonFileName, sendedTxJson)
            if err is not None:
                return None, BankerError(err.msg)
            return unSignJsonPath, None
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
        return None, BankerError(e.msg)


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


def GetBalance(account):
    if account is None:
        return None, BankerError('account cannot be none')
    if account.getAddress() == '':
        return None, BankerError('account address cannot be empty')
    account, err = query(account)
    if err is not None:
        return None, BankerError(err)
    return account.getCoins(), None


def QueryAccountInfo(account):
    if account.getAddress() == '':
        return None
    try:
        resp = http.request(HTTP_METHOD_GET,
                            ACCOUNT_INFO_URL % (account.getAddress()))
        if resp.status == 200:
            jsonData = json.loads(resp.data)
            if jsonData and dict(jsonData).get('result') and (
                    dict(jsonData)['result']).get('value') and ((dict(
                        jsonData)['result'])['value']).get('address') == '':
                return None
            elif ((dict(jsonData)['result'])['value']
                  ).get('address') == account.getAddress():
                account.setAccNum(
                    (dict(jsonData)['result'])['value'].get('account_number'))
                account.setSequence(
                    (dict(jsonData)['result'])['value'].get('sequence'))
                coins = (dict(jsonData)['result'])['value'].get('coins')
                if coins and len(coins) > 0:
                    account.setCoins(coins)
                return account
            elif resp.status == 500 and dict(json.loads(
                    resp.data)).get('error'):
                return None
            else:
                return None
    except Exception as e:
        print(e)
        return None


class BankerError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def Error(self):
        return self.msg

    def __str__(self):
        return self.msg
