import json

import pexpect
import urllib3
import yaml

from autotx import (HSN_CLIENT_PATH, HSN_LOCAL_ACCOUNT_PATH, PROJECT_CONFIG_DIR)
from autotx.auth.account import Account
from autotx.auth.validator import Validator
from autotx.utils.contants import HTTP_METHOD_GET

ACCOUNT_CONFIG_PATH = PROJECT_CONFIG_DIR + '/account.yaml'
authAccountUrl = 'http://172.38.8.89:1317/auth/accounts/%s'
VALIDATOR_URL_SET = [
    'http://172.38.8.89:1317/staking/validators?status=bonded',
    "http://172.38.8.89:1317/staking/validators?status=unbonding",
    'http://172.38.8.89:1317/staking/validators?status=unbonded'
]
http = urllib3.PoolManager()
HSN_CLI_SHOW_ACCOUNT = '%s keys show %s --home %s'


def CollectAccount():
    accountList = []
    accountConfigFile = open(ACCOUNT_CONFIG_PATH, 'r', encoding='utf-8')
    try:
        if accountConfigFile.readable():
            localAccountList = yaml.load(accountConfigFile.read())
            if localAccountList is not None and len(localAccountList) > 0:
                for localAccount in localAccountList:
                    account = Account(name=localAccount['name'],
                                      password=localAccount['password'],
                                      accType=localAccount['type'])
                    account = CollectAccountFromLocal(account)
                    if account is not None:
                        account = CollectAccountFromNet(account)
                        if account is not None:
                            accountList.append(account)
                return accountList
    finally:
        if accountConfigFile:
            accountConfigFile.close()


def CollectAccountFromLocal(account):
    localAccountStr = pexpect.run(
        HSN_CLI_SHOW_ACCOUNT %
        (HSN_CLIENT_PATH, account.getName(),
         HSN_LOCAL_ACCOUNT_PATH + '/' + account.getName()))
    localAccountDict = json.loads(localAccountStr)
    if localAccountDict is not None:
        account.setName(localAccountDict['name'])
        account.setAccType(localAccountDict['type'])
        account.setAddress(localAccountDict['address'])
        account.setPubkey(localAccountDict['pubkey'])
        return account
    return None


def CollectAccountFromNet(account):
    if account.getAddress() == '':
        return None
    try:
        resp = http.request(HTTP_METHOD_GET,
                            authAccountUrl % (account.getAddress()))
        if resp.status == 200:
            jsonData = json.loads(resp.data)
            if jsonData and dict(jsonData).get('result') and (
                    dict(jsonData)['result']).get('value') and ((dict(
                        jsonData)['result'])['value']).get('address') == '':
                return None
            elif ((dict(jsonData)['result'])['value']
                  ).get('address') == account.getAddress():
                account.setAccNum(
                    (dict(jsonData)['result'])['value'].get('account_number'))
                account.setSequence(
                    (dict(jsonData)['result'])['value'].get('sequence'))
                coins = (dict(jsonData)['result'])['value'].get('coins')
                if coins and len(coins) > 0:
                    account.setCoins(coins)
                return account
            elif resp.status == 500 and dict(json.loads(
                    resp.data)).get('error'):
                return None
            else:
                return None
    except Exception as e:
        print(e)
        return None


def CollectValidators():
    validators = []
    try:
        for url in VALIDATOR_URL_SET:
            resp = http.request(HTTP_METHOD_GET, url)
            if resp.status == 200:
                data = json.loads(resp.data.decode('utf-8'))
                if len(list(data['result'])) == 0:
                    continue
                for item in list(data['result']):
                    validator = Validator(
                        item['operator_address'], item['consensus_pubkey'],
                        item['jailed'], item['status'], item['tokens'],
                        item['delegator_shares'], item['description'],
                        item['unbonding_height'], item['unbonding_time'],
                        item['commission'], item['min_self_delegation'])
                    validators.append(validator)
            elif resp.status >= 500:
                print('CollectValidators: server error')
        return validators
    except Exception as e:
        print(e)
        return None
