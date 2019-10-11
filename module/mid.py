from hsnhub_tx.error.errors import IllegalError
from hsnhub_tx.module.moduletype import LegalLetterType, LegalTypeLetter, LegalType
midTemplate = '{mType}|{sn}'


def GenerateMID(moduleType, sn):
    if LegalType(moduleType) is False:
        return None, IllegalError(
            'module {mtype} is invalid'.format(mtype=moduleType))
    mTypeLetter = LegalTypeLetter[moduleType]
    mid = midTemplate.format(mType=mTypeLetter, sn=sn)
    return mid, None


def SplitMid(mid):
    if isinstance(mid, str) is False:
        return None, IllegalError('invalid MID')
    if len(mid) < 1:
        return None, IllegalError('invalid MID')
    letter = (str(mid).split('|'))[0]
    if LegalLetterType[letter] is None:
        return None, IllegalError('invalid mid type letter {letter}'.format(letter=letter))
    sn = (str(mid).split('|'))[1]
    if sn is None:
        return None, IllegalError('invalid mid')
    return [letter, sn], None


# 校验序列号合法性
def legalSN(sn):
    if str(sn).isdigit() is True:
        return True
    return False
