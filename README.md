# autotx

a automated tx script for hsn-devnet

## Installation

### Requirements

1. python3
2. pip3

### Configuration

1. /config/global.yaml

    hsn_client_path: `the path of your hsncli`

    hsn_server_path: `the path of your hsnd`

    hsn_local_account_path:  `the path of your account's package located in Local directory`

    node_lcd_server: `the <host>:<port> of your hsnhub lcd server`

    node_rpc_server: `the <host>:<port> of your hsnhub rpc server`

    ***Don't delete other fields even though they are empty**

2. /config/account.yaml

    ```yaml
    - {
        filePath: the path of your local account directory,
        name: the name of local account,
        password: the password of local account,
        type: local,
    }
    ```

3. Dependent package download

    ```shell
    /autotx$: pip3 install -r requirements.txt
    ```

### Run

```shell
/autotx$:cd simple
```

```shell
/autotx$:python3 main.py
```
