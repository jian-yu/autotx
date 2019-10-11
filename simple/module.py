from hsnhub_tx.module.sn import SNGenerator
from hsnhub_tx.module.mid import GenerateMID
from hsnhub_tx.module.moduletype import TYPE_BANK, TYPE_BROADCAST, TYPE_SIGN
from hsnhub_tx.bank.bank import Banker
from hsnhub_tx.sign.sign import Signer
from hsnhub_tx.broadcast.broadcast import BroadCaster

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
