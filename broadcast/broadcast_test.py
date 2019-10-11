import unittest
from hsnhub_tx.broadcast.broadcast import standardize
from hsnhub_tx.module.sn import SNGenerator
from hsnhub_tx.module.mid import GenerateMID
from hsnhub_tx.module.moduletype import TYPE_BROADCAST
from hsnhub_tx.broadcast.broadcast import BroadCaster, checkTx


class TestBroadcast(unittest.TestCase):
    def setUp(self):
        self.sn = SNGenerator(1, 0)
        mid = GenerateMID(TYPE_BROADCAST, self.sn.Get())
        self.broadCaster = BroadCaster(mid, 0)

    def test_standardize(self):
        body = '''{
  "type": "cosmos-sdk/StdTx",
  "value": {
    "msg": [
      {
        "type": "cosmos-sdk/MsgSend",
        "value": {
          "from_address": "hsn1j4yux0ytemqjmcd6z7dej7ermuw2hp9mgwu04a",
          "to_address": "hsn1zqxayv6qe50w6h3ynfj6tq9pr09r7rtuq565cl",
          "amount": [
            {
              "denom": "hsn",
              "amount": "5"
            }
          ]
        }
      }
    ],
    "fee": {
      "amount": [
        {
          "denom": "hsn",
          "amount": "1"
        }
      ],
      "gas": "100000"
    },
    "signatures": [
      {
        "pub_key": {
          "type": "tendermint/PubKeySecp256k1",
          "value": "Awc87jJrm2k5JKdmDDDvvfrvsTm+nn4MF3V2KY2hByDw"
        },
        "signature": "r53KS1dtupptxEo0wFXqN6qm2gRHqISgsUiIjjSq0LEdGp7opEzlCQC+WhHTDyMuFW3bD5yVas1nFFklBBv98w=="
      }
    ],
    "memo": "sent"
  }
}
'''
        standardizedBody, err = standardize(body, 'async')
        print(standardizedBody)
        self.assertIsNone(err)

    def test_broadcast(self):
        body = '''{
  "type": "cosmos-sdk/StdTx",
  "value": {
    "msg": [
      {
        "type": "cosmos-sdk/MsgSend",
        "value": {
          "from_address": "hsn1502lgkad0tnc2szdww0whpxs30szz03lj6n06q",
          "to_address": "hsn1aqwurs5jfu5z0z3k99tljt9csausdqrcaewjwv",
          "amount": [
            {
              "denom": "hsn",
              "amount": "5"
            }
          ]
        }
      }
    ],
    "fee": {
      "amount": [
        {
          "denom": "hsn",
          "amount": "1"
        }
      ],
      "gas": "100000"
    },
    "signatures": [
      {
        "pub_key": {
          "type": "tendermint/PubKeySecp256k1",
          "value": "AkJJcM8yCkBL/rvDQxqxEDCswuYmjMLJSty3BR4m4YFk"
        },
        "signature": "swYNOEX5h936+YppikFni8QTR6mtfw0m25QETQYGY5x3i7W8Oquw1lLktxReZz7MbTgzN6hIElvQxB3q+UV71g=="
      }
    ],
    "memo": "sent"
  }
}
'''
        txJson, err = self.broadCaster.BroadCastTx(body, 'sync')
        print(txJson)
        self.assertIsNone(err)

    def test_CheckTx(self):
        body = '{"height":"0","txhash":"7F8A3C49D7B39F4C509213AC7A6A3E7670BE40CD7D0A736570178B26F42180C9","raw_log":"[{\"msg_index\":0,\"success\":true,\"log\":\"\"}]","logs":[{"msg_index":0,"success":true,"log":""}]}'
        ok, err = checkTx(body)
        self.assertTrue(ok)
        print(err)


if __name__ == '__main__':
    unittest.main()
