import os
from pathlib import Path

from web3 import Web3

PROJECT_ID = '029890c5690243edbcb9fc201eb85164'
HTTP_INFURA_PROVIDER_URL = f'https://mainnet.infura.io/v3/{PROJECT_ID}'
WSS_INFURA_PROVIDER_URL = f'wss://mainnet.infura.io/ws/v3/{PROJECT_ID}'


class Connection:
    def __init__(self):
        # api key doesn't seem to work
        # and is unnecessary under current security settings 🤷‍
        provider_secret = Path(__file__).parent / 'infura-provider-secret.txt'
        with provider_secret.open() as fp:
            infura_api_key = fp.read().strip()
        os.environ['WEB3_INFURA_API_KEY'] = infura_api_key

        # Use websocket provider to access events instead of http
        # Http provider causes errors due to missing method:
        #   "*** ValueError: {'code': -32601, 'message': 'The method eth_newFilter does not exist/is not available'}"   # noqa: E501
        # provider = Web3.HTTPProvider(HTTP_INFURA_PROVIDER_URL)
        provider = Web3.WebsocketProvider(WSS_INFURA_PROVIDER_URL)
        self.w3 = Web3(provider)
        assert self.w3.isConnected()
