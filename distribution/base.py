from abc import ABCMeta, abstractmethod


class Distribute(metaclass=ABCMeta):
    # withdraw a reward from a validator
    @abstractmethod
    def WithdrawDelegatorOneReward(delegator, validator, fees, gas, gasAdjust):
        pass

    # withdraw delegator all reward
    @abstractmethod
    def WithdrawDelegatorAllReward(delegator, validator):
        pass

    # replace a delegator reward address
    @abstractmethod
    def ReplaceRewardAddress(delegator, newAddress):
        pass

    # withdraw a validator reward
    @abstractmethod
    def WithdrawValidatorReward(validator):
        pass

    # query a delegator reword from a validator
    @abstractmethod
    def QueryDelegatorRewardWithValidator(delegator, validator):
        pass
