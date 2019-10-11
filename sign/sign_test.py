import unittest
from autotx.auth.account import Account
from autotx.module.sn import SNGenerator
from autotx.module.mid import GenerateMID
from autotx.sign.sign import Signer
from autotx.module.moduletype import TYPE_SIGN


class TestSigner(unittest.TestCase):

    def setUp(self):
        self.sn = SNGenerator(1, 0)
        mid = GenerateMID(TYPE_SIGN, self.sn.Get())
        self.signer = Signer(mid, 0)
        self.__accounts = []
        account = Account('hsn4', '12345678', 'local', 3, 5, 'hsn1j4yux0ytemqjmcd6z7dej7ermuw2hp9mgwu04a', 'hsnpub1addwnpepqvrnem3jdwdkjwfy5anqcv80hhawlvfeh608urqhw4mznrdpqus0qehz2gq')
        self.__accounts.append(account)
        account = Account('hsn4', '123456', 'local', 3, 5, 'hsn1j4yux0ytemqjmcd6z7dej7ermuw2hp9mgwu04a', 'hsnpub1addwnpepqvrnem3jdwdkjwfy5anqcv80hhawlvfeh608urqhw4mznrdpqus0qehz2gq')
        self.__accounts.append(account)
        account = Account('hsn4', '78945612', 'local', 3, 5, 'hsn1j4yux0ytemqjmcd6z7dej7ermuw2hp9mgwu04a', 'hsnpub1addwnpepqvrnem3jdwdkjwfy5anqcv80hhawlvfeh608urqhw4mznrdpqus0qehz2gq')
        self.__accounts.append(account)

    def test_sign(self):
        unSignJsonPath = '/home/xzjianyu/goproject/src/github.com/hyperspeednetwork/hsnhub_test/unSign.json'
        for account in self.__accounts:
            data, err = self.signer.Sign(account, unSignJsonPath, 'tcp://172.38.8.89:26657')
            self.assertIsNone(err)
            print(data)


if __name__ == '__main__':
    unittest.main()
