# status 调度器状态以及检查调度器状态的相关操作
from autotx.utils.rwlock import RWLock
from autotx.log.logger import Logger
from autotx.utils.contants import LOG_TIME_FOEMAT
import time

SCHED_STATUS_UNINITIALIZED = 0
SCHED_STATUS_INITIALIZING = 1
SCHED_STATUS_INITIALIZED = 2
SCHED_STATUS_STARTING = 3
SCHED_STATUS_STARTED = 4
SCHED_STATUS_STOPPING = 5
SCHED_STATUS_STOPPED = 6


class CheckStatusError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


def CheckStatus(srcStatus, dstStatus):
    lock = RWLock()
    lock.acquire_write()
    try:
        # 情况一
        if srcStatus == SCHED_STATUS_INITIALIZING:
            print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('scheduler is initialing...'))
            return CheckStatusError(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('scheduler is initialing...'))
        elif srcStatus == SCHED_STATUS_STARTING:
            print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('scheduler is starting...'))
            return CheckStatusError(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('scheduler is starting...'))
        elif srcStatus == SCHED_STATUS_STOPPING:
            print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('scheduler is stopping...'))
            return CheckStatusError(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('scheduler is stopping...'))
        # 情况二
        elif srcStatus == SCHED_STATUS_UNINITIALIZED and (dstStatus == SCHED_STATUS_STARTING or dstStatus == SCHED_STATUS_STOPPING):
            print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('scheduler haven\'t been initialized!'))
            return CheckStatusError(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('scheduler haven\'t been initialized!'))
        # 情况三
        elif dstStatus == SCHED_STATUS_INITIALIZING:
            if srcStatus == SCHED_STATUS_STARTED:
                print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('scheduler has been started!'))
                return CheckStatusError(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('scheduler has been started!'))
        elif dstStatus == SCHED_STATUS_STARTING:
            if srcStatus == SCHED_STATUS_UNINITIALIZED:
                print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('scheduler is being uninitialized!'))
                return CheckStatusError(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('scheduler is being uninitialized!'))
            elif srcStatus == SCHED_STATUS_STARTED:
                print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('scheduler has been started!'))
                return CheckStatusError(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('scheduler has been started!'))
        elif dstStatus == SCHED_STATUS_STOPPING:
            if srcStatus != SCHED_STATUS_STARTED:
                print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('scheduler haven\'t start!'))
                return CheckStatusError(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('scheduler haven\'t start!'))
        else:
            print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('unknown status'))
            return CheckStatusError(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('unknown status'))
        return None
    finally:
        if lock:
            lock.release()


def GetStatusDescription(status):
    if status == SCHED_STATUS_UNINITIALIZED:
        return 'UNINITIALIZED'
    elif status == SCHED_STATUS_INITIALIZING:
        return 'INITIALIZING'
    elif status == SCHED_STATUS_INITIALIZED:
        return 'INITIALIZED'
    elif status == SCHED_STATUS_STARTING:
        return 'STARTING'
    elif status == SCHED_STATUS_STARTED:
        return 'STARTED'
    elif status == SCHED_STATUS_STOPPING:
        return 'STOPPING'
    elif status == SCHED_STATUS_STOPPED:
        return 'STOPPED'
    else:
        return 'UNKNOWN'
