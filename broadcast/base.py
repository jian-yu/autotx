from abc import ABCMeta, abstractmethod


class BroadCast(metaclass=ABCMeta):
    @abstractmethod
    def BroadCastTx(self, body):
        pass
