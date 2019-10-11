import json


def GenBaseReqJson(fromAddr, chainId, accNum, sequence,  fees, simulate, memo='', gas='20000', gasAdjust='1.2'):
    if fromAddr is None or chainId is None or accNum is None or sequence is None or fees is None or simulate is None:
        return None, ArgsError('args insufficient!')
    if len(fees) == 0:
        return None, ArgsError('fees is invalid')
    data = {'from': fromAddr, 'memo': memo, 'chain_id': chainId, 'account_number': accNum, 'sequence': sequence, 'gas': gas, 'gas_adjustment': gasAdjust, 'fees': fees, 'simulate': simulate}
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
