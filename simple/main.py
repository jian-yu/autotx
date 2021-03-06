import time

from autotx.auth.auth import Auth
from autotx.auth.collect import CollectAccount, CollectValidators
from autotx.log.logger import Logger
from autotx.scheduler.args import ModuleArgs, PoolArgs
from autotx.scheduler.scheduler import Scheduler
from autotx.simple.module import GetBankers, GetBroadcasters, GetSigners, GetStakingers, GetDistributors
from autotx.utils.contants import LOG_TIME_FOEMAT
from autotx import HSN_NODE_RPC_SERVER


def main():
    scheduler = Scheduler()
    poolArgs = PoolArgs(50, 10, 50, 10, 50, 10, 50, 10, 50, 10, 50, 100)
    bankers, err = GetBankers(1)
    if err is not None:
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('An error occurs when building banker: %s' % (err)))
    signers, err = GetSigners(1)
    if err is not None:
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('An error occurs when building signer: %s' % (err)))
    broadcasters, err = GetBroadcasters(1)
    if err is not None:
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('An error occurs when building broadcaster: %s' % (err)))
    stakingers, err = GetStakingers(1)
    if err is not None:
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('An error occurs when building stakinger: %s' % (err)))
    distributors, err = GetDistributors(1)
    if err is not None:
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('An error occurs when building distributor: %s' % (err)))
    moduleArgs = ModuleArgs(bankers, signers, broadcasters, stakingers, distributors)

    err = scheduler.Init(moduleArgs, poolArgs, HSN_NODE_RPC_SERVER)
    if err is not None:
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('An error occurs when initializing scheduler: %s' % (err)))

    # 收集本地账户并验证
    accountList = CollectAccount()
    print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Info('have %d account located at local' % (len(accountList))))
    auth = Auth('AUTH|100', 0)
    auth.Add(accountList)
    # 获取验证者
    validators = CollectValidators()
    auth.AddValidatorSet(validators)
    err = scheduler.Start(auth)
    if err is not None:
        print(Logger(time.strftime(LOG_TIME_FOEMAT, time.localtime())).Warn('An error occurs when starting scheduler: %s' % (err)))


if __name__ == "__main__":
    main()
