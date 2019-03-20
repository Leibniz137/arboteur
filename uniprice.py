"""
NOTE: requires Infura api key stored in ./infura-provider-secret.txt
"""
import json
import os
from pathlib import Path

from web3 import Web3


DAI_EXCHANGE_ADDR = '0x09cabec1ead1c0ba254b09efb3ee13841712be14'
USDC_EXCHANGE_ADDR = '0x97deC872013f6B5fB443861090ad931542878126'

PROJECT_ID = '029890c5690243edbcb9fc201eb85164'
HTTP_INFURA_PROVIDER_URL = f'https://mainnet.infura.io/v3/{PROJECT_ID}'
WSS_INFURA_PROVIDER_URL = f'wss://mainnet.infura.io/ws/v3/{PROJECT_ID}'

PROVIDER_FEE_PERCENT = 0.003
NUM_DAYS_BACK_TO_CALCULATE = 720
USDC_TOKEN_DECIMALS = 6


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


def calculate_pool(w3, contract):
    current_eth_total = 0
    current_token_total = 0
    MARKET_CREATION_BLOCK = 7101817
    events = contract.events

    liquidity_adds = events.AddLiquidity.createFilter(fromBlock=MARKET_CREATION_BLOCK).get_all_entries()   # noqa: E501
    for event in liquidity_adds:
        eth = event['args']['eth_amount'] / 1e18
        tokens = event['args']['token_amount'] / 10**USDC_TOKEN_DECIMALS
        current_eth_total += eth
        current_token_total += tokens

    liquidity_removals = events.RemoveLiquidity.createFilter(fromBlock=MARKET_CREATION_BLOCK).get_all_entries()   # noqa: E501
    for event in liquidity_removals:
        eth = event['args']['eth_amount'] / 1e18
        tokens = event['args']['token_amount'] / 10**USDC_TOKEN_DECIMALS
        current_eth_total -= eth
        current_token_total -= tokens

    token_purchases = events.TokenPurchase.createFilter(fromBlock=MARKET_CREATION_BLOCK).get_all_entries()   # noqa: E501
    for event in token_purchases:
        eth = event['args']['eth_sold'] / 1e18
        tokens = event['args']['tokens_bought'] / 10**USDC_TOKEN_DECIMALS
        current_eth_total += eth
        current_token_total -= tokens

    eth_purchases = events.EthPurchase.createFilter(fromBlock=MARKET_CREATION_BLOCK).get_all_entries()   # noqa: E501
    for event in eth_purchases:
        eth = event['args']['eth_bought'] / 1e18
        tokens = event['args']['tokens_sold'] / 10**USDC_TOKEN_DECIMALS
        current_eth_total -= eth
        current_token_total += tokens

    return (current_eth_total, current_token_total)


def get_eth_to_token_price(eth_reserve, token_reserve):
    input_eth_with_fee = 1 - PROVIDER_FEE_PERCENT
    numerator = input_eth_with_fee * token_reserve
    denominator = eth_reserve + input_eth_with_fee
    rate = float(numerator) / float(denominator)
    return rate if rate > 0 else 0


def main(exchange_addr=USDC_EXCHANGE_ADDR):
    # api key doesn't seem to work/unnecessary under current security settings
    provider_secret = Path(__file__).parent / 'infura-provider-secret.txt'
    with provider_secret.open() as fp:
        infura_api_key = fp.read().strip()
    os.environ['WEB3_INFURA_API_KEY'] = infura_api_key

    # Use websocket provider to access events instead of http
    # Http provider causes errors due to missing method:
    #   "*** ValueError: {'code': -32601, 'message': 'The method eth_newFilter does not exist/is not available'}"   # noqa: E501
    # provider = Web3.HTTPProvider(HTTP_INFURA_PROVIDER_URL)
    provider = Web3.WebsocketProvider(WSS_INFURA_PROVIDER_URL)
    w3 = Web3(provider)
    assert w3.isConnected()

    address = w3.toChecksumAddress(exchange_addr)
    json_path = Path(__file__).parent / 'exchangeABI.json'
    with json_path.open() as fp:
        abi = json.load(fp)
    contract = w3.eth.contract(address=address, abi=abi)
    (eth_reserve, token_reserve) = calculate_pool(w3, contract)
    exchange_rate = get_eth_to_token_price(eth_reserve, token_reserve)
    return exchange_rate


if __name__ == '__main__':
    # print(calculate_dataset())
    # print(main(DAI_EXCHANGE_ADDR))
    print(main(USDC_EXCHANGE_ADDR))
    # print(main('0x4e395304655F0796bc3bc63709DB72173b9DdF98'))
