import json
import time

import urllib3

from autotx import HSN_CHAIN_ID, UNSIGN_JSON_DIR
from autotx.bank.bank import GetBalance
from autotx.common.baseReq import GenBaseReqJson
from autotx.module.module import Module
from autotx.bank.bank import QueryAccountInfo
from autotx.staking.base import Staking
from autotx.staking.req import GenDelegateTxJson
from autotx.utils.contants import HTTP_METHOD_GET, HTTP_METHOD_POST, DELEGATOR_DELEGATE_URL, DELEGATOR_UNBONDING_DELEGATE_URL
from autotx.utils.file import WriteToFile
from autotx.utils.timestamp import now_timestamp

http = urllib3.PoolManager()


class Stakinger(Module, Staking):
    def __init__(self, mid, calculateCost):
        super(Stakinger, self).__init__(mid, calculateCost)

    def Delegate(self, delegator, validator, coin, fees, gas, gasAdjust):
        self.IncrHandingCount()
        self.IncrCalledCount()
        now = now_timestamp()
        try:
            avaliableBalance, err = GetAvailableBalance(delegator)
            if err is not None:
                return None, DelegatorError(err.msg)
            if avaliableBalance < int(coin['amount']):
                return None, DelegatorError(
                    'avaliable hsn token is insufficient!')
            memo = '%s delegate %s hsn to %s' % (delegator.getAddress(), coin['amount'],
                                                 validator.operatorAddr)
            delegator = QueryAccountInfo(delegator)
            # 获取账户最新信息
            if delegator is None:
                return None, DelegatorError('delegator is invalid!')
            baseReqJson, err = GenBaseReqJson(delegator, HSN_CHAIN_ID, fees,
                                              False, memo, gas, gasAdjust)
            if err is not None:
                return None, err
            delegateTxJson, err = GenDelegateTxJson(baseReqJson, delegator,
                                                    validator, coin)
            if err is not None:
                return None, err
            delegatedTxJson, err = postDelegate(delegateTxJson,
                                                delegator.getAddress())
            if err is not None:
                return None, err
            # 写入到文件中
            unSignJsonFileName = '[delegate]--' + delegator.getAddress() + '|' + str(int(round(time.time() * 1000))) + '.json'
            unSignJsonPath, err = WriteToFile(UNSIGN_JSON_DIR,
                                              unSignJsonFileName,
                                              delegatedTxJson)
            if err is not None:
                return None, DelegatorError(err.msg)
            return unSignJsonPath, None
        finally:
            self.SetCalculateCost(now_timestamp() - now)
            self.DecrHandingCount()

    def Redelegate(self, reDelegation):
        pass

    def UnbondingDelegate(self, unDelegation):
        pass


def GetAvailableBalance(delegator):
    if delegator is None or delegator.getAddress() == '':
        return None, DelegatorError('args is invalid')
    delegatedToken = 0
    unbondingToken = 0
    balance = 0
    # get delegator's delegated token
    try:
        resp = http.request(HTTP_METHOD_GET,
                            DELEGATOR_DELEGATE_URL % (delegator.getAddress()))
        if resp.status == 200:
            data = json.loads(resp.data.decode('utf-8'))
            delegations = list(data['result'])
            if len(delegations) > 0:
                for delegation in delegations:
                    delegatedToken += int((delegation['balance'])['amount'])
        else:
            return None, DelegatorError('server error')
    except Exception as e:
        return None, DelegatorError(e.msg)
    # get delegator's unbonding token
    try:
        resp = http.request(
            HTTP_METHOD_GET,
            DELEGATOR_UNBONDING_DELEGATE_URL % (delegator.getAddress()))
        if resp.status == 200:
            data = json.loads(resp.data.decode('utf-8'))
            unbondingDelegations = list(data['result'])
            if len(delegations) > 0:
                for unbondingDelegation in unbondingDelegations:
                    entries = list(unbondingDelegation['entries'])
                    if len(entries) > 0:
                        for entry in entries:
                            unbondingToken += int(entry['balance'])
    except Exception as e:
        return None, DelegatorError(e.msg)
    coins, err = GetBalance(delegator)
    if err is not None:
        return None, DelegatorError(err.msg)
    # get delegator's balance
    balance = int(coins['hsn'])
    return balance - delegatedToken - unbondingToken, None


def postDelegate(body, delegatorAddr):
    try:
        resp = http.request(HTTP_METHOD_POST,
                            DELEGATOR_DELEGATE_URL % (delegatorAddr),
                            body=body)
        if resp and resp.status == 200:
            return resp.data.decode('utf-8'), None
        elif resp and resp.status == 400:
            return None, DelegatorError('Invalid request')
        elif resp and resp.status == 500:
            return None, DelegatorError('Server internal error')
        else:
            return None, DelegatorError('Unknown error')
    except Exception as e:
        return None, DelegatorError(e)


class DelegatorError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def Error(self):
        return self.msg

    def __str__(self):
        return self.msg
