import json
import time

import urllib3

from autotx import HSN_CHAIN_ID, UNSIGN_JSON_DIR
from autotx.bank.bank import QueryAccountInfo
from autotx.common.baseReq import GenBaseReqJson
from autotx.distribution.base import Distribute
from autotx.module.module import Module
from autotx.utils.contants import HTTP_METHOD_GET, HTTP_METHOD_POST
from autotx.utils.file import WriteToFile
from autotx.utils.timestamp import now_timestamp
from autotx.distribution.req import GenWithdrawDelegatorOneRewardTxJson
from decimal import Decimal

http = urllib3.PoolManager()

DELEGATOR_REWARD_URL = 'http://172.38.8.89:1317/distribution/delegators/%s/rewards/%s'


class Distributor(Module, Distribute):

    def WithdrawDelegatorOneReward(self, delegator, validator, fees, gas, gasAdjust):
        self.IncrHandingCount()
        self.IncrCalledCount()
        now = now_timestamp()
        try:
            rewards, err = self.QueryDelegatorRewardWithValidator(delegator, validator)
            if err is not None:
                return None, DistributorError('WithdrawDelegatorOneReward: ' + err.msg)
            memo = '%s withdraw reward from %s' % (delegator.getAddress(), validator.operatorAddr)
            if rewards:
                if len(rewards) == 0:
                    return None, DistributorError('WithdrawDelegatorOneReward: ' + 'reward is empty')
                for reward in rewards:
                    if reward['denom'] == 'hsn':
                        if Decimal(reward['amount']) == Decimal('0'):
                            return None, DistributorError('WithdrawDelegatorOneReward: ' + 'reward is 0')
                delegator = QueryAccountInfo(delegator)
                # 获取账户最新信息
                if delegator is None:
                    return None, DistributorError('WithdrawDelegatorOneReward: ' + 'delegator is invalid!')
                baseReqJson, err = GenBaseReqJson(delegator, HSN_CHAIN_ID, fees, False, memo, gas, gasAdjust)
                if err is not None:
                    return None, DistributorError('WithdrawDelegatorOneReward: ' + err.msg)
                withdrawTxJson, err = GenWithdrawDelegatorOneRewardTxJson(baseReqJson)
                if err is not None:
                    return None, DistributorError('WithdrawDelegatorOneReward: ' + err.msg)
                withdrawnTxJson, err = postWithdrawDelegatorOneReward(withdrawTxJson, delegator.getAddress(), validator.operatorAddr)
                if err is not None:
                    return None, DistributorError('WithdrawDelegatorOneReward: ' + err.msg)
                # 写入到文件中
                unSignJsonFileName = '[withdrawreward]--' + delegator.getAddress() + '|' + str(int(round(time.time() * 1000))) + '.json'
                unSignJsonPath, err = WriteToFile(UNSIGN_JSON_DIR, unSignJsonFileName, withdrawnTxJson)
                if err is not None:
                    return None, DistributorError(err.msg)
                return unSignJsonPath, None
            return None, DistributorError('WithdrawDelegatorOneReward: ' + 'reward is invalid!')
        finally:
            self.SetCalculateCost(now_timestamp() - now)
            self.DecrHandingCount()

    def WithdrawDelegatorAllReward(self, delegator, validator):
        pass

    def ReplaceRewardAddress(self, delegator, newAddress):
        pass

    def WithdrawValidatorReward(self, delegator):
        pass

    def QueryDelegatorRewardWithValidator(self, delegator, validator):
        self.IncrHandingCount()
        self.IncrCalledCount()
        try:
            resp = http.request(HTTP_METHOD_GET, DELEGATOR_REWARD_URL % (delegator.getAddress(), validator.operatorAddr))
            if resp.status == 200:
                data = json.loads(resp.data.decode('utf-8'))
                return data['result'], None
            elif resp.status == 400:
                return None, DistributorError(data['Invalid delegator address'])
            elif resp.status == 500:
                data = json.loads(resp.data.decode('utf-8'))
                return None, DistributorError(data['error'])
        except Exception as e:
            return None, e
        finally:
            self.DecrHandingCount()


def postWithdrawDelegatorOneReward(body, delegatorAddr, validatorOpeAddr):
    try:
        resp = http.request(HTTP_METHOD_POST, DELEGATOR_REWARD_URL % (delegatorAddr, validatorOpeAddr), body=body)
        if resp and resp.status == 200:
            return resp.data.decode('utf-8'), None
        elif resp and resp.status == 400:
            return None, DistributorError('postWithdrawDelegatorOneReward: Invalid request')
        elif resp and resp.status == 500:
            return None, DistributorError('postWithdrawDelegatorOneReward: Server internal error')
        else:
            return None, DistributorError('postWithdrawDelegatorOneReward: Unknown error')
    except Exception as e:
        return None, e


class DistributorError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def Error(self):
        return self.msg

    def __str__(self):
        return self.msg
