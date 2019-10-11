import unittest
from autotx.bank.bank import Banker
from autotx.module.sn import SNGenerator
from autotx.module.mid import GenerateMID
from autotx.module.moduletype import TYPE_BANK
from autotx.auth.account import Account


class TestBanker(unittest.TestCase):
    def setUp(self):
        self.sn = SNGenerator(1, 0)
        mid = GenerateMID(TYPE_BANK, self.sn.Get())
        self.banker = Banker(mid, 0)
        self.srcAccount = Account('hsn1', '12345678', 'local', 0, 14, 'hsn1p8hqjcsxat30zgllpdkvgtutctrhun70uv9ts0', 'hsnpub1addwnpepqvfe59jmpyjqxjkez68gh3f60utmljpzhfm29af9z98n758zpqns7m4aj02')
        self.dstAccount = Account('hsn1', '12345678', 'local', 1, 4, 'hsn13eje6wryqzxj03tymd6uunx7653v9pru7qc9w0', 'hsnpub1addwnpepqvu2j4u64ajpg94zqzdtucsfc74dd4keq3d7p93mp8qspt086kzdvxvvclw')

    def test_getBalance(self):
        coins, err = self.banker.GetBalance(self.srcAccount)
        print(coins)
        self.assertIsNone(err)

    def test_sendCoins(self):
        sendedTxJsonFilePath, err = self.banker.SendCoins(self.srcAccount, self.dstAccount, [{'denom': 'hsn', 'amount': '5'}], [{'denom': 'hsn', 'amount': '1'}], '100000', '1.0')
        print(sendedTxJsonFilePath)
        self.assertIsNone(err)


if __name__ == '__main__':
    unittest.main()
