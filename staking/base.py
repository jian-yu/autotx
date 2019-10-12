from abc import ABCMeta, abstractmethod


class Delegate(metaclass=ABCMeta):
    # Delegate delegator must be a invalid account, coin must is a amount of hsn
    @abstractmethod
    def Delegate(self, delegator, validator, coin):
        pass

    @abstractmethod
    def Redelegate(self, delegation):
        pass

    @abstractmethod
    def UnbondingDelegate(self, delegation):
        pass
