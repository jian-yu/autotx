from abc import ABCMeta, abstractmethod
from hsnhub_tx.error.errors import IllegalError, EmptyError
from hsnhub_tx.module.mid import SplitMid
from hsnhub_tx.module.moduletype import LegalLetterType
from hsnhub_tx.module.moduletype import CheckType
from hsnhub_tx.module.moduletype import LegalType
from hsnhub_tx.utils.balance import Select
from hsnhub_tx.utils.rwlock import RWLock


class Registry(metaclass=ABCMeta):
    # 注册模块
    @abstractmethod
    def Register(self, module):
        pass

    # 注销模块
    @abstractmethod
    def UnRegister(self, mid):
        pass

    # 获取一个指定类型的实例(根据处理时间快慢评分)
    @abstractmethod
    def Get(self, mType):
        pass

    # 获取指定类型的所有实例
    @abstractmethod
    def GetAllByType(self, moduleType):
        pass

    # 获取所有实例
    @abstractmethod
    def GetAll(self):
        pass

    # 清除所有注册实例
    @abstractmethod
    def Clear(self):
        pass


class Registrar(Registry):
    def __init__(self):
        self.__moduleTypeDict = {}
        self.__rwLock = RWLock()

    def Register(self, module):
        if module is None:
            return False, IllegalError('module is none')
        mid = module.ID()
        separateMID, err = SplitMid(mid)
        if err is not None:
            return False, IllegalError('invalid mid: {mid}'.format(mid=mid))
        mType = LegalLetterType[list(separateMID)[0]]
        if CheckType(mType, module) is False:
            return False, IllegalError(
                'invalid module type: {mType}'.format(mType=mType))
        # 加写锁
        self.__rwLock.acquire_write()
        try:
            modules = self.__moduleTypeDict.get(mType)
            if modules is None:
                modules = {}
            if modules.get(mid) is not None:
                return False, None
            modules[mid] = module
            self.__moduleTypeDict[mType] = modules
            return True, None
        finally:
            self.__rwLock.release()

    def UnRegister(self, mid):
        if mid is None or str(mid) == '':
            return False, IllegalError('empty mid')
        separateMID, err = SplitMid(mid)
        if err is not None:
            return False, IllegalError('invalid mid: {mid}'.format(mid=mid))
        mType = LegalLetterType[list(separateMID)[0]]
        # 加读锁
        self.__rwLock.acquire_read()
        try:
            modules = self.__moduleTypeDict[mType]
            if modules is not None:
                if modules[mid] is not None:
                    del modules[mid]
            return True, None
        finally:
            self.__rwLock.release()

    def Get(self, moduleType):
        modules, err = self.GetAllByType(moduleType)
        if err is not None:
            return None, err
        costs = {}
        for mid, module in modules.items():
            costs[mid] = module.CalculateCost()
        costArr = costs.items()
        index = Select(list(costArr))  # 筛选出更优的实例
        selectModuleID = list(costArr)[index][0]
        return modules[selectModuleID], None

    def GetAllByType(self, mType):
        if LegalType(mType) is False:
            return None, IllegalError(
                'invalid module type: {mType}'.format(mType=mType))
        # 加读锁
        self.__rwLock.acquire_read()
        try:
            modules = self.__moduleTypeDict[mType]
            if len(modules) == 0:
                return None, EmptyError()
            result = {}
            for mid, module in modules.items():
                result[mid] = module
            return result, None
        finally:
            self.__rwLock.release()

    def GetAll(self):
        result = {}
        # 加读锁
        self.__rwLock.acquire_read()
        try:
            for i, modules in self.__moduleTypeDict:
                for mid, module in modules:
                    result[mid] = module
            return result
        finally:
            self.__rwLock.release()

    def Clear(self):
        # 加读锁
        self.__rwLock.acquire_read()
        try:
            del self.__moduleTypeDict
            self.__moduleTypeDict = {}
        finally:
            self.__rwLock.release()
