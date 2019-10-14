from queue import Queue, Full, Empty
from autotx.utils.rwlock import RWLock


class Buffer:
    def __init__(self, size):
        self.__queue = Queue(size)
        self.__closed = 0
        self.__rwlock = RWLock()

    def Cap(self):
        return self.__queue.maxsize

    def Len(self):
        return self.__queue.qsize()

    def Put(self, data):
        self.__rwlock.acquire_read()
        try:
            if self.Closed():
                return False, BufferClosedError()
            self.__queue.put_nowait(data)
            return True, None
        except Full:
            return False, None
        finally:
            self.__rwlock.release()

    def Get(self):
        try:
            if self.Closed() is True:
                return None, BufferClosedError()
            item = self.__queue.get_nowait()
            return item, None
        except Empty:
            return None, None

    def Close(self):
        self.__rwlock.acquire_write()
        try:
            if self.__closed == 0:
                self.__closed = 1
                self.__queue = None
                return True
            return False
        finally:
            self.__rwlock.release()

    def Closed(self):
        return self.__closed != 0 or self.__queue is None


class BufferClosedError(Exception):
    def __init__(self):
        self.msg = 'buffer had been closed!'

    def __str__(self):
        return self.msg
