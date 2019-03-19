"""
NOTE: requires Infura api key stored in ./infura-provider-secret.txt
"""
import json
import os
from pathlib import Path

from web3 import Web3


DAI_EXCHANGE_ADDR = '0x09cabec1ead1c0ba254b09efb3ee13841712be14'
USDC_EXCHANGE_ADDR = '0x97deC872013f6B5fB443861090ad931542878126'
FACTORY_ADDR = '0xc0a47dFe034B400B47bDaD5FecDa2621de6c4d95'

PROJECT_ID = '029890c5690243edbcb9fc201eb85164'
HTTP_INFURA_PROVIDER_URL = f'https://mainnet.infura.io/v3/{PROJECT_ID}'
WSS_INFURA_PROVIDER_URL = f'wss://mainnet.infura.io/ws/v3/{PROJECT_ID}'

PROVIDER_FEE_PERCENT = 0.003
NUM_DAYS_BACK_TO_CALCULATE = 720


class Exchange:
    def __init__(self, contract):
        self.contract = contract

    @property
    def rate(self):
        """
        get current exchange rate per eth
        NOTE: this doesnt seem to work for usdc
        """
        return self.contract.functions.getEthToTokenInputPrice(1).call()


def calculate_dataset():
    for days_back in range(NUM_DAYS_BACK_TO_CALCULATE, -1, -1):
        print(days_back)


def get_eth_to_token_price(eth_reserve, token_reserve):
    input_eth_with_fee = 1 - PROVIDER_FEE_PERCENT
    numerator = input_eth_with_fee * token_reserve
    denominator = eth_reserve + input_eth_with_fee
    rate = float(numerator) / float(denominator)
    return rate if rate > 0 else 0


def main(exchange_addr):
    provider_secret = Path(__file__).parent / 'infura-provider-secret.txt'
    with provider_secret.open() as fp:
        infura_api_key = fp.read().strip()
    os.environ['WEB3_INFURA_API_KEY'] = infura_api_key
    # provider = Web3.HTTPProvider(HTTP_INFURA_PROVIDER_URL)
    provider = Web3.WebsocketProvider(WSS_INFURA_PROVIDER_URL)
    w3 = Web3(provider)
    assert w3.isConnected()

    address = w3.toChecksumAddress(FACTORY_ADDR)
    json_path = Path(__file__).parent / 'factoryABI.json'
    with json_path.open() as fp:
        abi = json.load(fp)
    factory = w3.eth.contract(address=address, abi=abi)

    address = w3.toChecksumAddress(exchange_addr)
    json_path = Path(__file__).parent / 'exchangeABI.json'
    with json_path.open() as fp:
        abi = json.load(fp)
    contract = w3.eth.contract(address=address, abi=abi)
    exchange = Exchange(contract)
    return exchange.rate


if __name__ == '__main__':
    # print(calculate_dataset())
    # print(main(DAI_EXCHANGE_ADDR))
    print(main(USDC_EXCHANGE_ADDR))
    # print(main('0x4e395304655F0796bc3bc63709DB72173b9DdF98'))
