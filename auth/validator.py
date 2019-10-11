class Validator:
    def __init__(self, operatorAddr, conspub, jailed, status, tokens, delegatorShares, description, unbondingHeight, unbondingTime, commission, minSelfDelegation):
        self.operatorAddr = operatorAddr
        self.conspub = conspub
        self.jailed = jailed
        self.status = status
        self.tokens = tokens
        self.delegatorShares = delegatorShares
        self.description = description
        self.unbondingHeight = unbondingHeight
        self.unbondingTime = unbondingHeight
        self.commission = commission
        self.minSelfDelegation = minSelfDelegation

def GetValidator():