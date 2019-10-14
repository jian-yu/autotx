import unittest

from autotx.auth.account import Account
from autotx.auth.validator import Validator
from autotx.distribution.distribution import Distributor
from autotx.module.mid import GenerateMID
from autotx.module.moduletype import TYPE_DISTRIBUTION
from autotx.module.sn import SNGenerator


class TestDistribution(unittest.TestCase):
    def setUp(self):
        self.sn = SNGenerator(1, 0)
        mid = GenerateMID(TYPE_DISTRIBUTION, self.sn.Get())
        self.distributor = Distributor(mid, 0)
        self.delegator = Account('hsn1', '12345678', 'local', '0', '64', 'hsn1p8hqjcsxat30zgllpdkvgtutctrhun70uv9ts0', 'hsnpub1addwnpepqvfe59jmpyjqxjkez68gh3f60utmljpzhfm29af9z98n758zpqns7m4aj02')
        self.validator = Validator(
            'hsnvaloper1p8hqjcsxat30zgllpdkvgtutctrhun70fyw3q3', 'hsnvalconspub1zcjduepqjlzvnup2xvanh94yf40eadzfs4e57tc63n0qlg8m6wjs8urq25esqkwnd3', False, 2, '3189846465', '3189846465.000000000000000000',
            {'moniker': 'node1', 'identity': '', 'website': '', 'details': ''}, '0', '1970-01-01T00:00:00Z',
            {'commission_rates': {'rate': '0.100000000000000000', 'max_rate': '0.200000000000000000', 'max_change_rate': '0.010000000000000000'}, 'update_time': '2019-08-24T08:51:45.550141024Z'},
            '1'
        )

    def test_withdrawReward(self):
        withdrawRewardTxFilePath, err = self.distributor.WithdrawDelegatorOneReward(self.delegator, self.validator, [{'denom': 'hsn', 'amount': '1'}], '100000', '1.0')
        print(withdrawRewardTxFilePath)
        self.assertIsNone(err)
