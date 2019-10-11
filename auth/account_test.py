from autotx.auth.account import Account
import unittest


class TestAccount(unittest.TestCase):
    def setUp(self):
        account = Account('hsn1', '12345678', '0', '14', 'hsn1p8hqjcsxat30zgllpdkvgtutctrhun70uv9ts0', 'local', 'hsnpub1addwnpepqvfe59jmpyjqxjkez68gh3f60utmljpzhfm29af9z98n758zpqns7m4aj02')
        account.setCoin(('hsn', '100000'))
        self.account = account

    def test_account(self):
        self.assertEqual(self.account.getName(), 'hsn1')
        self.assertEqual(self.account.getPassword(), '12345678')
        self.assertEqual(self.account.getAccNum(), '0')
        self.assertEqual(self.account.getSequence(), '14')
        self.assertEqual(self.account.getAddress(), 'hsn1p8hqjcsxat30zgllpdkvgtutctrhun70uv9ts0')
        self.assertEqual(self.account.getAccType(), 'local')
        self.assertEqual(self.account.getPubkey(), 'hsnpub1addwnpepqvfe59jmpyjqxjkez68gh3f60utmljpzhfm29af9z98n758zpqns7m4aj02')
        self.assertEqual((self.account.GetCoin())['hsn'], '100000')


if __name__ == '__main__':
    unittest.main()
