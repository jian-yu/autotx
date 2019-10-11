import unittest

from autotx.auth.account import Account
from autotx.auth.auth import Auth, checkAccount
from autotx.auth.collect.collect import CollectAccount, CollectValidators
from autotx.module.sn import SNGenerator


class TestAuth(unittest.TestCase):

    def setUp(self):
        self.sn = SNGenerator(1, 0)

    def test_CheckAccount(self):
        account = Account(
            'hsn1', '12345678', '0', '14',
            'hsn1p8hqjcsxat30zgllpdkvgtutctrhun70uv9ts0', 'local',
            'hsnpub1addwnpepqvfe59jmpyjqxjkez68gh3f60utmljpzhfm29af9z98n758zpqns7m4aj02'
        )
        ok, err = checkAccount(account)
        self.assertTrue(ok)

    def test_collectAccount(self):
        CollectAccount()

    def test_colletValidator(self):
        auth = Auth(1, 0)
        validators = CollectValidators()
        auth.AddValidatorSet(validators)
        print(validators)
        print(auth.GetValidatorDict)
        self.assertGreater(len(validators), 0)


if __name__ == '__main__':
    unittest.main()
