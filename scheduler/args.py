class PoolArgs:
    def __init__(self, bankerBufCap, bankerMaxBufNumber, signerBufCap, signerBufMaxNumber, broadcasterBufCap, broadcasterMaxNumber, stakingBufCap, stakingMaxNumber, errorBufCap, errorMaxNumber):
        self.BankerBufCap = bankerBufCap
        self.BankerMaxBufNumber = bankerMaxBufNumber
        self.SignerBufCap = signerBufCap
        self.SignerBufMaxNumber = signerBufMaxNumber
        self.BroadcasterBufCap = broadcasterBufCap
        self.BroadcasterMaxNumber = broadcasterMaxNumber
        self.StakingBufCap = stakingBufCap
        self.StakingMaxNumber = stakingMaxNumber
        self.ErrorBufCap = errorBufCap
        self.ErrorMaxNumber = errorMaxNumber

    def Check(self):
        if self.BankerBufCap == 0:
            return PoolArgsError('zero banker buffer capacity')
        if self.BankerMaxBufNumber == 0:
            return PoolArgsError('zero banker max buffer number')
        if self.SignerBufCap == 0:
            return PoolArgsError('zero signer buffer capacity')
        if self.SignerBufMaxNumber == 0:
            return PoolArgsError('zero signer max buffer number')
        if self.BroadcasterBufCap == 0:
            return PoolArgsError('zero broadcaster buffer capacity')
        if self.BroadcasterMaxNumber == 0:
            return PoolArgsError('zero broadcaster max buffer number')
        if self.StakingBufCap == 0:
            return PoolArgsError('zero staking buffer capacity')
        if self.StakingMaxNumber == 0:
            return PoolArgsError('zero staking max buffer number')
        if self.ErrorBufCap == 0:
            return PoolArgsError('zero error buffer capacity')
        if self.ErrorMaxNumber == 0:
            return PoolArgsError('zero error max buffer number')
        return None


class PoolArgsError(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


class ModuleArgs:
    def __init__(self, bankers, signers, broadcasters, stakings):
        self.Bankers = bankers
        self.Signers = signers
        self.Broadcasters = broadcasters
        self.Stakings = stakings

    def Check(self):
        if len(self.Bankers) == 0:
            return ModuleArgsError('empty banker list')
        if len(self.Signers) == 0:
            return ModuleArgsError('empty signer list')
        if len(self.Broadcasters) == 0:
            return ModuleArgsError('empty broadcaster list')
        if len(self.Stakings) == 0:
            return ModuleArgsError('empty staking list')
        return None


class ModuleArgsError(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


class SendCoinArgs:
    def __init__(self, srcAccount, dstAccount, coins, fees, gas, gasAdjust):
        self.srcAccount = srcAccount
        self.dstAccount = dstAccount
        self.coins = coins
        self.fees = fees
        self.gas = gas
        self.gasAdjust = gasAdjust

    def Check(self):
        if self.srcAccount is None or self.srcAccount.getAddress() == '':
            return SendCoinArgsError('srcAccount is invalid')
        if self.dstAccount is None or self.dstAccount.getAddress() == '':
            return SendCoinArgsError('dstAccount is invalid')
        if self.coins is None or len(self.coins) == 0:
            return SendCoinArgsError('empty coins')
        if self.fees is None or len(self.fees) == 0:
            return SendCoinArgsError('empty fess')
        if self.gas is None:
            return SendCoinArgsError('empty gas')
        if self.gasAdjust is None:
            return SendCoinArgsError('empty gasAdjust')
        return None


class SendCoinArgsError(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


class SendSignArgs:
    def __init__(self, srcAccount, sendedJsonFilePath, node):
        self.srcAccount = srcAccount
        self.sendedJsonFilePath = sendedJsonFilePath
        self.node = node

    def Check(self):
        if self.srcAccount is None or self.srcAccount.getAddress() == '':
            return SendSignArgsError('srcAccount is invalid')
        if self.sendedJsonFilePath is None:
            return SendSignArgsError('empty sendedJsonFilePath')
        if self.node is None:
            return SendSignArgsError('empty node')
        return None


class SendSignArgsError(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


class SendBroadcastArgs:
    def __init__(self, srcAccount, body, mode='sync'):
        self.srcAccount = srcAccount
        self.body = body
        self.mode = mode

    def Check(self):
        if self.body is None:
            return SendBroadcastArgsError('empty broadcast body')
        if self.srcAccount is None:
            return SendBroadcastArgsError('unknown tx src account')
        return None


class SendBroadcastArgsError(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


class DelegateArgs():
    def __init__(self, delegator, validator, coin, fees, gas, gasAdjust):
        self.delegator = delegator
        self.validator = validator
        self.coin = coin
        self.fees = fees
        self.gas = gas
        self.gasAdjust = gasAdjust

    def Check(self):
        if self.delegator is None or self.delegator.getAddress() == '':
            return DelegateArgsError('delegator is invalid')
        if self.validator is None:
            return DelegateArgsError('validator is invalid')
        if self.coin is None:
            return DelegateArgsError('empty coins')
        if self.fees is None or len(self.fees) == 0:
            return DelegateArgsError('empty fess')
        if self.gas is None:
            return DelegateArgsError('empty gas')
        if self.gasAdjust is None:
            return DelegateArgsError('empty gasAdjust')
        return None


class StakingArgs():
    def __init__(self, _type, data):
        self._type = _type
        self.data = data

    def getType(self):
        return self._type

    def getData(self):
        return self.data


class DelegateArgsError(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message
