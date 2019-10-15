from autotx.module.module import Module
from autotx.utils.rwlock import RWLock
from autotx.auth.account import Account
import urllib3
from autotx.utils.contants import HTTP_METHOD_GET, AUTH_ACCOUNT_URL
import json
from autotx.error.errors import AccountNotFoundError, AccountParseError, UnknownError
from autotx import PROJECT_DIR

http = urllib3.PoolManager()
AUTH_LOG_FILE_PATH = PROJECT_DIR + '/auth/log/auth.log'


class Auth(Module):
    def __init__(self, mid, calculateCost):
        super(Auth, self).__init__(mid, calculateCost)
        self.__rwLock = RWLock()
        self.__accountDict = {}
        self.__validatorDict = {}

    def __addAccount(self, account):
        self.IncrHandingCount()
        self.IncrCalledCount()
        self.__rwLock.acquire_write()
        try:
            ok, err = checkAccount(account)
            if ok is True:
                self.__accountDict[account.getAddress()] = account
                self.IncrAcceptedCount()
                return True, None
            return False, err
        finally:
            self.DecrHandingCount()
            self.__rwLock.release()

    def DelAccount(self, account):
        self.IncrHandingCount()
        self.IncrCalledCount()
        self.__rwLock.acquire_write()
        try:
            account = Account(account)
            del self.__accountDict[account.getAddress()]
            self.IncrAcceptedCount()
        finally:
            self.DecrHandingCount()
            self.__rwLock.release()

    def __addAccountList(self, accountList):
        for account in accountList:
            self.__addAccount(account)

    def Add(self, accounts):
        if isinstance(accounts, list):
            self.__addAccountList(accounts)
        elif isinstance(accounts, Account):
            self.__addAccount(accounts)

    def GetAccountDict(self):
        self.IncrHandingCount()
        self.IncrCalledCount()
        try:
            self.IncrAcceptedCount()
            return self.__accountDict
        finally:
            self.DecrHandingCount()

    def AddValidatorSet(self, validators):
        self.IncrHandingCount()
        self.IncrCalledCount()
        self.__rwLock.acquire_write()
        try:
            for validator in validators:
                self.__validatorDict[validator.operatorAddr] = validator
            self.IncrAcceptedCount()
        finally:
            self.DecrHandingCount()
            self.__rwLock.release()

    def GetValidatorDict(self):
        self.IncrHandingCount()
        self.IncrCalledCount()
        try:
            self.IncrAcceptedCount()
            return self.__validatorDict
        finally:
            self.DecrHandingCount()


# 检查账户有效性
def checkAccount(account):
    try:
        resp = http.request(HTTP_METHOD_GET, AUTH_ACCOUNT_URL % (account.getAddress()))
        if resp.status == 200:
            jsonData = json.loads(resp.data.decode('utf8'))
            if jsonData and dict(jsonData).get('result') and (dict(jsonData)['result']).get('value') and ((dict(jsonData)['result'])['value']).get('address') == '':
                return False, AccountNotFoundError()
            elif ((dict(jsonData)['result'])['value']).get('address') == account.getAddress():
                return True, None
        elif resp.status == 500 and dict(json.loads(resp.data)).get('error'):
            return False, AccountParseError(dict(json.loads(resp.data)).get('error'))
        else:
            return False, UnknownError()
    except Exception as e:
        print(e)
        return False, Exception(e)
