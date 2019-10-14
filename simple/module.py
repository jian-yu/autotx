from autotx.module.sn import SNGenerator
from autotx.module.mid import GenerateMID
from autotx.module.moduletype import TYPE_BANK, TYPE_BROADCAST, TYPE_SIGN, TYPE_STAKING
from autotx.bank.bank import Banker
from autotx.sign.sign import Signer
from autotx.broadcast.broadcast import BroadCaster
from autotx.staking.staking import Stakinger

snGen = SNGenerator(1, 0)


def GetBankers(count):
    bankers = []
    if count == 0:
        return bankers, None
    for i in range(count):
        mid, err = GenerateMID(TYPE_BANK, snGen.Get())
        if err is not None:
            return bankers, err
        banker = Banker(mid, 0)
        bankers.append(banker)
    return bankers, None


def GetSigners(count):
    signers = []
    if count == 0:
        return signers, None
    for i in range(count):
        mid, err = GenerateMID(TYPE_SIGN, snGen.Get())
        if err is not None:
            return signers, err
        signer = Signer(mid, 0)
        signers.append(signer)
    return signers, None


def GetBroadcasters(count):
    broadcasters = []
    if count == 0:
        return broadcasters, None
    for i in range(count):
        mid, err = GenerateMID(TYPE_BROADCAST, snGen.Get())
        if err is not None:
            return broadcasters, err
        broadcaster = BroadCaster(mid, 0)
        broadcasters.append(broadcaster)
    return broadcasters, None


def GetStakingers(count):
    stakingers = []
    if count == 0:
        return stakingers, None
    for i in range(count):
        mid, err = GenerateMID(TYPE_STAKING, snGen.Get())
        if err is not None:
            return stakingers, err
        stakinger = Stakinger(mid, 0)
        stakingers.append(stakinger)
    return stakingers, None
