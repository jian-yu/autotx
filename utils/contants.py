from autotx import HSN_NODE_LCD_SERVER
# HTTP METHOOD
HTTP_METHOD_GET = 'GET'
HTTP_METHOD_POST = 'POST'
HTTP_METHOD_PUT = 'PUT'
HTTP_METHOD_DELETE = 'DELETE'

# DATE FORMAT
LOG_TIME_FOEMAT = '[%Y-%m-%d %H:%M:%S]'

# URL
AUTH_ACCOUNT_URL = HSN_NODE_LCD_SERVER + '/auth/accounts/%s'
VALIDATOR_URL_SET = [
    HSN_NODE_LCD_SERVER + '/staking/validators?status=bonded',
    HSN_NODE_LCD_SERVER + '/staking/validators?status=unbonding',
    HSN_NODE_LCD_SERVER + '/staking/validators?status=unbonded'
]
ACCOUNT_BALANCE_URL = HSN_NODE_LCD_SERVER + '/bank/balances/%s'
SEND_TX_URL = HSN_NODE_LCD_SERVER + '/bank/accounts/%s/transfers'
ACCOUNT_INFO_URL = HSN_NODE_LCD_SERVER + '/auth/accounts/%s'
BROADCAST_TX_URL = HSN_NODE_LCD_SERVER + '/txs'
DELEGATOR_REWARD_URL = HSN_NODE_LCD_SERVER + '/distribution/delegators/%s/rewards/%s'
TX_HASH_URL = HSN_NODE_LCD_SERVER + '/txs/%s'
DELEGATOR_DELEGATE_URL = HSN_NODE_LCD_SERVER + '/staking/delegators/%s/delegations'
DELEGATOR_UNBONDING_DELEGATE_URL = HSN_NODE_LCD_SERVER + '/staking/delegators/%s/unbonding_delegations'

# CLI
HSN_CLI_SHOW_ACCOUNT_COMMAND = '%s keys show %s --home %s'
SIGN_TX_COMMAND = '%s tx sign %s --from %s --node %s --home %s'