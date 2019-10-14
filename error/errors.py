ERROR_BANKER = 'banker error'
ERROR_SIGNER = 'signer error'
ERROR_BROADCASTER = 'broadcaster error'
ERROR_SCHEDULER = 'scheduler error'
ERROR_STAKINGER = 'stakinger error'
ERROR_DISTRIBUTION = 'distribution error'


class TxerError:
    def __init__(self, errType, errMsg):
        self.__errType = errType
        self.__errMsg = errMsg
        self.__fullErrMsg = ''

    def Type(self):
        return self.__errType

    def Error(self):
        if self.__fullErrMsg == '':
            pass
        return self.__fullErrMsg

    def FullErrMsg(self):
        str = 'Txer error '
        if self.__errType != '':
            str += '<'
            str += self.__errType
            str += "> "
        str += self.__errMsg
        self.__fullErrMsg = str
        return


class IllegalError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class EmptyError(Exception):
    def __init__(self, msg):
        self.msg = 'dst is empty'

    def __str__(self):
        return self.msg


class AccountNotFoundError(Exception):
    def __init__(self, name):
        self.msg = 'account %s is not found' % (name)

    def __str__(self):
        return self.msg


class AccountParseError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class UnknownError(Exception):
    def __init__(self):
        self.msg = 'unknown error'

    def __str__(self):
        return self.msg
