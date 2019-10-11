from queue import Queue, Empty
from hsnhub_tx.utils.buffer import Buffer
from hsnhub_tx.utils.rwlock import RWLock


class Pool:
    def __init__(self, bufCap, maxBufNumber):
        self.__bufCap = bufCap
        self.__maxBufNumber = maxBufNumber
        self.__bufNumber = 1
        self.__bufQueue = Queue(maxBufNumber)
        self.__closed = 0
        self.__rwlock = RWLock()
        self.__total = 0
        buf = Buffer(bufCap)
        self.__bufQueue.put_nowait(buf)

    def BufCap(self):
        return self.__bufCap

    def MaxBufNumber(self):
        return self.__maxBufNumber

    def BufNumber(self):
        return self.__bufNumber

    def Total(self):
        return self.__total

    def Put(self, data):
        if self.Closed():
            return BufferPoolClosedError('pool has been closed!')
        count = 0
        maxCount = self.BufNumber() * 5
        err = None
        ok = False
        while True:
            try:
                buf = self.__bufQueue.get_nowait()

                def putData(buf, data, maxCount):
                    ok = False
                    err = None
                    if self.Closed():
                        return ok, BufferPoolClosedError(
                            'pool has been closed!')
                    try:
                        ok, err = buf.Put(data)
                        if ok:
                            self.__rwlock.acquire_write()
                            try:
                                self.__total += 1
                                return ok, err
                            finally:
                                self.__rwlock.release()
                        if err:
                            return ok, err
                        # 缓冲器已满
                        nonlocal count
                        count += 1
                        if count >= maxCount and self.BufNumber(
                        ) < self.MaxBufNumber():
                            self.__rwlock.acquire_write()
                            if self.BufNumber() < self.MaxBufNumber():
                                if self.Closed():
                                    self.__rwlock.release()
                                    return ok, err
                                newBuffer = Buffer(self.BufCap())
                                newBuffer.Put(data)
                                self.__bufQueue.put_nowait(newBuffer)
                                self.__bufNumber += 1
                                self.__total += 1
                                ok = True
                            self.__rwlock.release()
                            count = 0
                    finally:
                        self.__rwlock.acquire_read()
                        if self.Closed():
                            self.__bufNumber -= 1
                            return ok, BufferPoolClosedError(
                                'pool has been closed!')
                        else:
                            self.__bufQueue.put_nowait(buf)
                        self.__rwlock.release()
                        return ok, err

                ok, err = putData(buf, data, maxCount)
                if ok or err is not None:
                    break
            except Empty:
                continue
        return err

    def Get(self):
        err = None
        data = None
        if self.Closed():
            return data, BufferPoolClosedError('pool has been closed!')
        count = 0
        maxCount = self.BufNumber() * 10
        while True:
            try:
                buf = self.__bufQueue.get_nowait()

                def getData(buf, maxCount):
                    data = None
                    err = None
                    nonlocal count
                    try:
                        if self.Closed():
                            return data, BufferPoolClosedError(
                                'pool has been closed!')
                        data, err = buf.Get()
                        if data is not None:
                            self.__rwlock.acquire_write()
                            self.__total -= 1
                            self.__rwlock.release()
                            return data, err
                        if err:
                            return data, err
                        count += 1
                        return data, err
                    finally:
                        if count >= maxCount and buf.Len(
                        ) == 0 and self.BufNumber() > 1:
                            buf.Close()
                            self.__rwlock.acquire_write()
                            self.__bufNumber -= 1
                            self.__rwlock.release()
                            count = 0
                            return data, err
                        self.__rwlock.acquire_read()
                        if self.Closed():
                            self.__bufNumber -= 1
                            err = BufferPoolClosedError(
                                'buffer pool is closed!')
                        else:
                            self.__bufQueue.put_nowait(buf)
                        self.__rwlock.release()

                data, err = getData(buf, maxCount)
                if data is not None or err is not None:
                    break
            except Empty:
                break
        return data, err

    def Close(self):
        self.__rwlock.acquire_write()
        try:
            if self.__closed == 0:
                self.__closed = 1
                while True:
                    try:
                        buffer = self.__bufQueue.get_nowait()
                        buffer.Close()
                    except Empty:
                        break
                self.__bufQueue = None
                return True
            return False
        finally:
            self.__rwlock.release()

    def Closed(self):
        return self.__closed == 1 or self.__bufQueue is None


class PoolIllegalParameterError(Exception):
    def __init__(self, msg):
        self.__message = msg

    def __str__(self):
        return self.__message


class BufferPoolClosedError(Exception):
    def __init__(self, msg):
        self.__message = msg

    def __str__(self):
        return self.__message
