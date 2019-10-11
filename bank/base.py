from abc import ABCMeta, abstractmethod


class Bank(metaclass=ABCMeta):

    # 查询账户资产
    @abstractmethod
    def GetBalance(self, account):
        pass

    # 发送代币
    @abstractmethod
    def SendCoins(self, srcAccount, dstAccount, fees, gas, gasAdjust):
        pass
