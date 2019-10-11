from hsnhub_tx.module.base import BasicModule
from hsnhub_tx.utils.rwlock import RWLock


class Module(BasicModule):

    def __init__(self, mid, calculateCost):
        self.__mid = mid
        self.__calculateCost = calculateCost
        self.__calledCount = 0
        self.__acceptedCount = 0
        self.__completedCount = 0
        self.__handingCount = 0
        self.__rwLock = RWLock()

    def ID(self):
        return self.__mid

    def CalledCount(self):
        self.__rwLock.acquire_read()
        try:
            return self.__calledCount
        finally:
            self.__rwLock.release()

    def AcceptedCount(self):
        self.__rwLock.acquire_read()
        try:
            return self.__acceptedCount
        finally:
            self.__rwLock.release()

    def CompletedCount(self):
        self.__rwLock.acquire_read()
        try:
            return self.__completedCount
        finally:
            self.__rwLock.release()

    def HandingCount(self):
        self.__rwLock.acquire_read()
        try:
            return self.__handingCount
        finally:
            self.__rwLock.release()

    def CalculateCost(self):
        self.__rwLock.acquire_read()
        try:
            return self.__calculateCost
        finally:
            self.__rwLock.release()

    def IncrCalledCount(self):
        self.__rwLock.acquire_write()
        try:
            self.__calledCount += 1
        finally:
            self.__rwLock.release()

    def IncrAcceptedCount(self):
        self.__rwLock.acquire_write()
        try:
            self.__acceptedCount += 1
        finally:
            self.__rwLock.release()

    def IncrCompletedCount(self):
        self.__rwLock.acquire_write()
        try:
            self.__completedCount += 1
        finally:
            self.__rwLock.release()

    def IncrHandingCount(self):
        self.__rwLock.acquire_write()
        try:
            self.__handingCount += 1
        finally:
            self.__rwLock.release()

    def DecrHandingCount(self):
        self.__rwLock.acquire_write()
        try:
            self.__handingCount -= 1
        finally:
            self.__rwLock.release()

    def SetCalculateCost(self, calculateCost):
        self.__rwLock.acquire_write()
        try:
            self.__calculateCost = calculateCost
        finally:
            self.__rwLock.release()

    def GetCalculateCost(self):
        self.__rwLock.acquire_read()
        try:
            return self.__calculateCost
        finally:
            self.__rwLock.release()

    def Counts(self):
        pass

    def Clear(self):
        self.__rwLock.acquire_write()
        try:
            self.__calledCount = 0
            self.__acceptedCount = 0
            self.__completedCount = 0
            self.__handingCount = 0
            self.__calculateCost = 0
        finally:
            self.__rwLock.release()
