"""
NOTE: requires Infura api key

$ export WEB3_INFURA_API_KEY='...'
"""
import json
from pathlib import Path

from web3 import Web3


DAI_EXCHANGE_ADDR = '0x09cabec1ead1c0ba254b09efb3ee13841712be14'
FACTORY = '0xc0a47dFe034B400B47bDaD5FecDa2621de6c4d95'

PROJECT_ID = '029890c5690243edbcb9fc201eb85164'
PROVIDER_URL = f'https://mainnet.infura.io/v3/{PROJECT_ID}'


class Exchange:
    def __init__(self, contract):
        self.contract = contract

    @property
    def rate(self):
        """
        get current exchange rate per eth
        """
        return self.contract.functions.getEthToTokenInputPrice(1).call()


def main():
    provider = Web3.HTTPProvider(PROVIDER_URL)
    w3 = Web3(provider)
    assert w3.isConnected()

    address = w3.toChecksumAddress(DAI_EXCHANGE_ADDR)
    json_path = Path(__file__).parent / 'exchangeABI.json'
    with json_path.open() as fp:
        abi = json.load(fp)
    dai_swap = w3.eth.contract(address=address, abi=abi)
    exchange = Exchange(dai_swap)
    return exchange.rate


if __name__ == '__main__':
    print(main())
