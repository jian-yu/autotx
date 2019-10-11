from abc import ABCMeta, abstractmethod
import sys
from autotx.utils.rwlock import RWLock


class SequenceNumberGenerator(metaclass=ABCMeta):
    # 序列号起始号码
    @abstractmethod
    def Start(self):
        pass

    # 序列号最大值
    @abstractmethod
    def Max(self):
        pass

    # 下一个序列号
    @abstractmethod
    def Next(self):
        pass

    # 循环计数
    @abstractmethod
    def CycleCount(self):
        pass

    # 获取一个序列号并产生下一个序列号
    @abstractmethod
    def Get(self):
        pass


class SNGenerator(SequenceNumberGenerator):

    def __init__(self, start, max):
        self.__start = start
        self.__max = max if max != 0 else sys.maxsize
        self.__next = start
        self.__rwLock = RWLock()

    def Start(self):
        return self.__start

    def Max(self):
        return self.__max

    def Next(self):
        self.__rwLock.acquire_read()
        try:
            return self.__next
        finally:
            self.__rwLock.release()

    def CycleCount(self):
        self.__rwLock.acquire_read()
        try:
            return self.__cycleCount
        finally:
            self.__rwLock.release()

    def Get(self):
        self.__rwLock.acquire_read()
        try:
            sn = self.__next
            if sn == self.__max:
                self.__next = self.__start
                self.__cycleCount += 1
            else:
                self.__next += 1
            return sn
        finally:
            self.__rwLock.release()
