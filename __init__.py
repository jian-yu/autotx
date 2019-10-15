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

HSN_NODE_LCD_SERVER = ''
HSN_NODE_RPC_SERVER = ''

LOCAL_ACCOUNTS_PATH = PROJECT_CONFIG_DIR + '/account.yaml'

config = {}


def init():
    try:
        globalConfig = open(PROJECT_CONFIG_DIR + '/global.yaml',
                            'r',
                            encoding='utf-8')
        if globalConfig.readable():
            global config
            config = yaml.load(globalConfig.read())
            global HSN_CLIENT_PATH, HSN_SERVER_PATH, HSN_LOCAL_ACCOUNT_PATH, HSN_CHAIN_ID, HSN_UNSIGN_JSON_DIR, HSN_NODE_LCD_SERVER, HSN_NODE_RPC_SERVER, LOCAL_ACCOUNTS_PATH
            HSN_CLIENT_PATH = config['hsn_client_path']
            HSN_SERVER_PATH = config['hsn_server_path']
            HSN_LOCAL_ACCOUNT_PATH = config['hsn_local_account_path']
            HSN_CHAIN_ID = config['chain_id']
            HSN_NODE_LCD_SERVER = config['node_lcd_server']
            HSN_NODE_RPC_SERVER = config['node_rpc_server']
            initFileDir(config)
            if config.get('local_accounts_path') is not None and config['local_accounts_path'] != '':
                LOCAL_ACCOUNTS_PATH = config['local_accounts_path']
    finally:
        if globalConfig:
            globalConfig.close()


def initFileDir(config):
    global UNSIGN_JSON_DIR, BROADCASTED_TX_DIR, PROJECT_DIR
    if config.get('unsign_dir') is not None and config['unsign_dir'] != '':
        UNSIGN_JSON_DIR = config['unsign_dir']
    if config.get('broadcasted_tx_dir'
                  ) is not None and config['broadcasted_tx_dir'] != '':
        BROADCASTED_TX_DIR = config['broadcasted_tx_dir']
    if not os.path.isdir(UNSIGN_JSON_DIR):
        os.makedirs(UNSIGN_JSON_DIR)
    if not os.path.isdir(BROADCASTED_TX_DIR):
        os.makedirs(BROADCASTED_TX_DIR)


init()
