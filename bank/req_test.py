from hsnhub_tx.bank.req import GenSendTxJson
from hsnhub_tx.common.baseReq import GenBaseReqJson
from hsnhub_tx.auth.account import Account
from hsnhub_tx import HSN_CHAIN_ID
import unittest


class TestReq(unittest.TestCase):
    def setUp(self):
        self.account = Account('hsn1', '12345678', 'local', 0, 14, 'hsn1p8hqjcsxat30zgllpdkvgtutctrhun70uv9ts0', 'hsnpub1addwnpepqvfe59jmpyjqxjkez68gh3f60utmljpzhfm29af9z98n758zpqns7m4aj02')

    def test_SendTxReq(self):
        baseReqJson, err = GenBaseReqJson(self.account.getAddress(), HSN_CHAIN_ID, str(self.account.getAccNum()), str(self.account.getSequence()), [{'denom': 'hsn', 'amount': '10'}], False, 'send money', '20000', '1.0')
        self.assertIsNone(err)
        sendTxReq, err = GenSendTxJson(baseReqJson, [{'demon': 'hsn', 'amount': '50'}])
        print(sendTxReq)
        self.assertIsNone(err)


if __name__ == '__main__':
    unittest.main()