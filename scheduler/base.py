from abc import ABCMeta, abstractclassmethod


class Schedule(metaclass=ABCMeta):

    # 初始化调度器
    @abstractclassmethod
    def Init(self, modules):
        pass

    # 启动调度器
    @abstractclassmethod
    def Start(self):
        pass

    # 停止调度器
    @abstractclassmethod
    def Stop(self):
        pass

    # 调度器状态
    @abstractclassmethod
    def Status(self):
        pass

    # 错误队列
    @abstractclassmethod
    def ErrorQueue(self):
        pass
