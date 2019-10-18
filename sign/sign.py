from autotx.sign.base import Sign
from autotx.module.module import Module
import pexpect
from autotx import HSN_CLIENT_PATH, HSN_LOCAL_ACCOUNT_PATH
from autotx.utils.contants import SIGN_TX_COMMAND
from autotx.utils.timestamp import now_timestamp

ERROR_INVALID_ACCOUNT_PASSWORD = 'ERROR: invalid account password'
ERROR_ACCOUNT_PASSWORD_INSUFFICIENT_CHARACTERS = 'ERROR: Error reading passphrase: password must be at least 8 characters'


class Signer(Module, Sign):
    def __init__(self, mid, calculateCost):
        super(Signer, self).__init__(mid, calculateCost)

    def Sign(self, account, unSignTxJsonPath, node):
        self.IncrHandingCount()
        self.IncrCalledCount()
        now = now_timestamp()
        try:
            signedJson, err = sign(account, unSignTxJsonPath, node)
            if err is not None:
                return None, err
            self.IncrCompletedCount()
            return signedJson, None
        finally:
            self.SetCalculateCost(now_timestamp() - now)
            self.DecrHandingCount()


def sign(account, unSignTxJsonPath, node):
    try:
        child = pexpect.spawnu(SIGN_TX_COMMAND % (HSN_CLIENT_PATH, unSignTxJsonPath, account.getName(), node, HSN_LOCAL_ACCOUNT_PATH + '/' + account.getName()))
        child.expect('(?i)Password to sign with \'%s\':' % (account.getName()))
        child.sendline(account.getPassword())
        child.expect(pexpect.EOF)
        data = child.before
        if data == ERROR_INVALID_ACCOUNT_PASSWORD:
            return None, SignerError(ERROR_INVALID_ACCOUNT_PASSWORD)
        elif data == ERROR_ACCOUNT_PASSWORD_INSUFFICIENT_CHARACTERS:
            return None, SignerError(ERROR_ACCOUNT_PASSWORD_INSUFFICIENT_CHARACTERS)
        else:
            return data, None
    except pexpect.EOF:
        return None, SignerError('pexpect eof')
    except pexpect.TIMEOUT:
        return None, SignerError('pexpect timeout')


class SignerError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class ParseError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
