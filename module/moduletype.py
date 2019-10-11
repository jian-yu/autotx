from hsnhub_tx.error.errors import IllegalError

TYPE_AUTH = 'auth'
TYPE_BANK = 'bank'
TYPE_DISTRIBUTION = 'distribution'
TYPE_STAKING = 'staking'
TYPE_SIGN = 'sign'
TYPE_BROADCAST = 'broadcast'

LegalTypeLetter = {
    TYPE_AUTH: 'AUTH',
    TYPE_BANK: 'BANK',
    TYPE_DISTRIBUTION: 'DISTRIBUTION',
    TYPE_STAKING: 'STAKING',
    TYPE_SIGN: 'SIGN',
    TYPE_BROADCAST: 'BROADCAST'
}

LegalLetterType = {
    'AUTH': TYPE_AUTH,
    'BANK': TYPE_BANK,
    'DISTRIBUTION': TYPE_DISTRIBUTION,
    'STAKING': TYPE_STAKING,
    'SIGN': TYPE_SIGN,
    'BROADCAST': TYPE_BROADCAST
}


def CheckType(moduleType, module):
    if module is None or moduleType == '':
        return False
    if moduleType == TYPE_AUTH:
        return True
    elif moduleType == TYPE_BANK:
        return True
    elif moduleType == TYPE_DISTRIBUTION:
        return True
    elif moduleType == TYPE_STAKING:
        return True
    elif moduleType == TYPE_SIGN:
        return True
    elif moduleType == TYPE_BROADCAST:
        return True
    return False


def LegalType(moduleType):
    if LegalTypeLetter[moduleType] is not None:
        return True
    return False


# 获取mid的类型 return type, error
def GetType(mid):
    from hsnhub_tx.module.mid import SplitMid
    separateMID, err = SplitMid(mid)
    if err is not None:
        return None, err
    mType = LegalLetterType[list(separateMID)[0]]
    if mType is None:
        return None, IllegalError('invalid mid: {mid}'.format(mid=mid))
    return mType, None
