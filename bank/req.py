import json


def GenSendTxJson(baseReq, amount):
    if baseReq is None or amount is None:
        return None, ArgsError('args are insufficient')
    if len(amount) == 0:
        return None, ArgsError('amount cannot be empty')
    baseReqJsonObj = json.loads(baseReq)
    if baseReqJsonObj is None:
        return None, ParseError('json parse error')
    data = {'base_req': baseReqJsonObj, 'amount': amount}
    jsonData = json.dumps(data)
    if jsonData is None:
        return None, ParseError('json parse error')
    return jsonData, None


class ArgsError(Exception):
    def __init__(self, msg):
        self.__message = msg

    def __str__(self):
        return self.__message


class ParseError(Exception):
    def __init__(self, msg):
        self.__message = msg

    def __str__(self):
        return self.__message
