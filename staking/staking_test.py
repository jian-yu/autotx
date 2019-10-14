import unittest
from autotx.staking.staking import Stakinger
from autotx.auth.validator import Validator
from autotx.module.sn import SNGenerator
from autotx.module.mid import GenerateMID
from autotx.module.moduletype import TYPE_STAKING
from autotx.auth.account import Account


class TestDelegate(unittest.TestCase):
    def setUp(self):
        self.sn = SNGenerator(1, 0)
        mid = GenerateMID(TYPE_STAKING, self.sn.Get())
        self.stakinger = Stakinger(mid, 0)
        self.delegator = Account('hsn1', '12345678', 'local', '0', '32', 'hsn1p8hqjcsxat30zgllpdkvgtutctrhun70uv9ts0', 'hsnpub1addwnpepqvfe59jmpyjqxjkez68gh3f60utmljpzhfm29af9z98n758zpqns7m4aj02')
        self.validator = Validator(
            'hsnvaloper1p8hqjcsxat30zgllpdkvgtutctrhun70fyw3q3', 'hsnvalconspub1zcjduepqjlzvnup2xvanh94yf40eadzfs4e57tc63n0qlg8m6wjs8urq25esqkwnd3', False, 2, '3189846465', '3189846465.000000000000000000',
            {'moniker': 'node1', 'identity': '', 'website': '', 'details': ''}, '0', '1970-01-01T00:00:00Z',
            {'commission_rates': {'rate': '0.100000000000000000', 'max_rate': '0.200000000000000000', 'max_change_rate': '0.010000000000000000'}, 'update_time': '2019-08-24T08:51:45.550141024Z'},
            '1'
        )
        pass

    def test_delegate(self):
        delegateJsonFilePath, err = self.stakinger.Delegate(self.delegator, self.validator, {'denom': 'hsn', 'amount': '50'}, [{'denom': 'hsn', 'amount': '1'}], '100000', '1.0')
        print(delegateJsonFilePath)
        self.assertIsNone(err)


if __name__ == '__main__':
    unittest.main()
