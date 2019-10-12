import json


def GenDelegateTxJson(baseReq, delegator, validator, coin):
    if baseReq is None:
        return None, ArgsError('args are insufficient')
    baseReqJsonObj = json.loads(baseReq)
    if baseReqJsonObj is None:
        return None, ParseError('json parse error')
    data = {'base_req': baseReqJsonObj, 'delegator_address': delegator.getAddress(), 'validator_address': validator.operatorAddr, 'amount': coin}
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
