from abc import ABCMeta, abstractmethod


class Sign(metaclass=ABCMeta):

    @abstractmethod
    def Sign(self, account, txBody):
        pass
