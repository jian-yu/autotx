from autotx.broadcast.base import BroadCast
from autotx.module.module import Module
import json
import urllib3
from autotx.utils.contants import HTTP_METHOD_POST
from autotx.utils.timestamp import now_timestamp

http = urllib3.PoolManager()
BROADCAST_TX_URL = 'http://172.38.8.89:1317/txs'


class BroadCaster(Module, BroadCast):
    def __init__(self, mid, calculateCost):
        super(BroadCaster, self).__init__(mid, calculateCost)

    def BroadCastTx(self, body, mode='sync'):
        self.IncrHandingCount()
        self.IncrHandingCount()
        now = now_timestamp()
        try:
            standardizedBody, err = standardize(body, mode)
            if err is not None:
                return None, BroadCasterError(err)
            broadCastTxJson, err = broadCastTx(standardizedBody)
            if err is not None:
                return None, BroadCasterError(err)
            self.IncrCompletedCount()
            return broadCastTxJson, None
        finally:
            self.SetCalculateCost(now_timestamp() - now)
            self.DecrHandingCount()


def standardize(body, mode):
    data = json.loads(body)
    if data is None:
        return None, ParseError('standardize: json.loads: json parse error')
    msg = (data['value'])['msg']
    fee = (data['value'])['fee']
    signatures = (data['value'])['signatures']
    memo = (data['value'])['memo']
    jsonData = json.dumps({'tx': {'msg': msg, 'fee': fee, 'signatures': signatures, 'memo': memo}, 'mode': mode})
    if data is None:
        return None, ParseError('standardize: json.dumps: json parse error')
    return jsonData, None


def broadCastTx(body):
    bct = json.loads(body)
    if bct is None:
        return None, ParseError('broadCastTx: json.loads: json parse error')
    if len((bct['tx'])['msg']) == 0:
        return None, BroadCasterError('msg is empty')
    if len((bct['tx'])['signatures']) == 0:
        return None, BroadCasterError('signatures is empty')
    if bct.get('mode') is None:
        return None, BroadCasterError('mode(sync/async/block) cannot be empty')
    try:
        resp = http.request(HTTP_METHOD_POST, BROADCAST_TX_URL, body=body)
        if resp and resp.status == 200:
            return resp.data.decode('utf-8'), None
        elif resp and resp.status == 500:
            jsonData = json.loads(resp.data)
            if jsonData and jsonData['error']:
                return None, BroadCasterError((jsonData['error'])['message'])
        else:
            return None, BroadCasterError('unknown error')
    except Exception as e:
        return None, BroadCasterError(e)


class BroadCasterError(Exception):
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
