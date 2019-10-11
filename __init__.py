import os
import yaml
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_CONFIG_DIR = PROJECT_DIR + '/config'
UNSIGN_JSON_DIR = PROJECT_DIR + '/unsign_json'
BROADCASTED_TX_DIR = PROJECT_DIR + '/broadcasted_tx'

HSN_CLIENT_PATH = ''
HSN_SERVER_PATH = ''
HSN_LOCAL_ACCOUNT_PATH = ''
HSN_CHAIN_ID = ''

config = {}


def init():
    try:
        globalConfig = open(PROJECT_CONFIG_DIR + '/global.yaml', 'r', encoding='utf-8')
        if globalConfig.readable():
            global config
            config = yaml.load(globalConfig.read())
            global HSN_CLIENT_PATH
            global HSN_SERVER_PATH
            global HSN_LOCAL_ACCOUNT_PATH
            global HSN_CHAIN_ID
            global HSN_UNSIGN_JSON_DIR
            HSN_CLIENT_PATH = config['hsn_client_path']
            HSN_SERVER_PATH = config['hsn_server_path']
            HSN_LOCAL_ACCOUNT_PATH = config['hsn_local_account_path']
            HSN_CHAIN_ID = config['chain_id']
    finally:
        if globalConfig:
            globalConfig.close()


init()
