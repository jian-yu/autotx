import threading

from queue import Queue


class RWLock:
    def __init__(self):
        self.wait_writers_q = Queue()
        self.rwlock = 0
        self.writers_waiting = 0
        self.monitor = threading.RLock()
        self.readers_ok = threading.Condition(self.monitor)

    def acquire_read(self):

        self.monitor.acquire()
        while self.rwlock < 0 or self.writers_waiting:
            self.readers_ok.wait()
        self.rwlock += 1
        self.monitor.release()

    def acquire_write(self):
        self.monitor.acquire()
        while self.rwlock != 0:
            self.writers_waiting += 1
            writers_ok = threading.Condition(self.monitor)
            self.wait_writers_q.put(writers_ok)
            writers_ok.wait()
            self.writers_waiting -= 1
        self.rwlock = -1
        self.monitor.release()

    def promote(self):
        self.monitor.acquire()
        self.rwlock -= 1
        while self.rwlock != 0:
            self.writers_waiting += 1
            writers_ok = threading.Condition(self.monitor)
            self.wait_writers_q.put(writers_ok)
            writers_ok.wait()
            self.writers_waiting -= 1
        self.rwlock = -1
        self.monitor.release()

    def demote(self):
        self.monitor.acquire()
        self.rwlock = 1
        self.readers_ok.notifyAll()
        self.monitor.release()

    def release(self):
        self.monitor.acquire()
        if self.rwlock < 0:
            self.rwlock = 0
        else:
            self.rwlock -= 1
        wake_writers = self.writers_waiting and self.rwlock == 0
        wake_readers = self.writers_waiting == 0
        self.monitor.release()
        if wake_writers:
            writers_ok = self.wait_writers_q.get_nowait()
            writers_ok.acquire()
            writers_ok.notify()
            writers_ok.release()
        elif wake_readers:
            self.readers_ok.acquire()
            self.readers_ok.notifyAll()
            self.readers_ok.release()
