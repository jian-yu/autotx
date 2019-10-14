import json


def GenWithdrawDelegatorOneRewardTxJson(baseReq):
    if baseReq is None:
        return None, ArgsError('args are insufficient')
    baseReqJsonObj = json.loads(baseReq)
    if baseReqJsonObj is None:
        return None, ParseError('json parse error')
    data = {'base_req': baseReqJsonObj}
    jsonData = json.dumps(data)
    if jsonData is None:
        return None, ParseError('json parse error')
    return jsonData, None


class ArgsError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class ParseError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
