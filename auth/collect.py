import json

import pexpect
import urllib3
import yaml

from autotx import (HSN_CLIENT_PATH, HSN_LOCAL_ACCOUNT_PATH, PROJECT_CONFIG_DIR)
from autotx.auth.account import Account
from autotx.auth.validator import Validator
from autotx.utils.contants import HTTP_METHOD_GET
from autotx.bank.bank import QueryAccountInfo

ACCOUNT_CONFIG_PATH = PROJECT_CONFIG_DIR + '/account.yaml'
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
                        account = QueryAccountInfo(account)
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
