from abc import ABCMeta, abstractmethod


class BasicModule(metaclass=ABCMeta):
    # 模块实例ID
    @abstractmethod
    def ID(self):
        pass

    # 模块被调用次数
    @abstractmethod
    def CalledCount(self):
        pass

    # 模块被调用接受次数
    @abstractmethod
    def AcceptedCount(self):
        pass

    # 模块被成功调用的次数
    @abstractmethod
    def CompletedCount(self):
        pass

    # 模块正则被调用次数
    @abstractmethod
    def HandingCount(self):
        pass

    # 所有调用次数
    @abstractmethod
    def Counts(self):
        pass

    # 模块实例计算开销（根据实例处理一个任务时间长短计算出开销）
    @abstractmethod
    def CalculateCost(self):
        pass
