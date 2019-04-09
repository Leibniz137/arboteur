"""
NOTE: requires Infura api key stored in ./infura-provider-secret.txt
"""
import math

import web3_infura
import uniswap
from uniswap import (
    USDC_EXCHANGE_ADDR,
    USDC_MARKET_CREATION_BLOCK,
    USDC_TOKEN_DECIMALS,
    PROVIDER_FEE_PERCENT,
)

NUM_DAYS_BACK_TO_CALCULATE = 720


def calculate_pool(w3, contract):
    current_eth_total = 0
    current_token_total = 0
    events = contract.events

    liquidity_adds = events.AddLiquidity.createFilter(fromBlock=USDC_MARKET_CREATION_BLOCK).get_all_entries()   # noqa: E501
    for event in liquidity_adds:
        eth = event['args']['eth_amount'] / 1e18
        tokens = event['args']['token_amount'] / 10**USDC_TOKEN_DECIMALS
        current_eth_total += eth
        current_token_total += tokens

    liquidity_removals = events.RemoveLiquidity.createFilter(fromBlock=USDC_MARKET_CREATION_BLOCK).get_all_entries()   # noqa: E501
    for event in liquidity_removals:
        eth = event['args']['eth_amount'] / 1e18
        tokens = event['args']['token_amount'] / 10**USDC_TOKEN_DECIMALS
        current_eth_total -= eth
        current_token_total -= tokens

    token_purchases = events.TokenPurchase.createFilter(fromBlock=USDC_MARKET_CREATION_BLOCK).get_all_entries()   # noqa: E501
    for event in token_purchases:
        eth = event['args']['eth_sold'] / 1e18
        tokens = event['args']['tokens_bought'] / 10**USDC_TOKEN_DECIMALS
        current_eth_total += eth
        current_token_total -= tokens

    eth_purchases = events.EthPurchase.createFilter(fromBlock=USDC_MARKET_CREATION_BLOCK).get_all_entries()   # noqa: E501
    for event in eth_purchases:
        eth = event['args']['eth_bought'] / 1e18
        tokens = event['args']['tokens_sold'] / 10**USDC_TOKEN_DECIMALS
        current_eth_total -= eth
        current_token_total += tokens

    return (current_eth_total, current_token_total)


def calculate_exchange_rate(eth_reserve, token_reserve):
    input_eth_with_fee = 1 - PROVIDER_FEE_PERCENT
    numerator = input_eth_with_fee * token_reserve
    denominator = eth_reserve + input_eth_with_fee
    rate = float(numerator) / float(denominator)
    return rate if rate > 0 else 0


def how_much_eth_to_buy(current_eth_reserve, current_token_reserve, target_exchange_rate):   # noqa: E501
    """

    """
    # TODO: why is this quadratic? is this correct?
    # TODO: if it is correct, which one to pick, positive or negative?
    input_eth_with_fee = 1 - PROVIDER_FEE_PERCENT
    constant_product = current_eth_reserve * current_token_reserve

    inside_sqrt = input_eth_with_fee**2 - 4*-(input_eth_with_fee * constant_product / target_exchange_rate)   # noqa: E501

    positive_target_eth_reserve = (
        -input_eth_with_fee + math.sqrt(inside_sqrt)
        /
        2
    )

    negative_target_eth_reserve = (
        -input_eth_with_fee - math.sqrt(inside_sqrt)
        /
        2
    )

    return (
        current_eth_reserve - positive_target_eth_reserve,
        current_eth_reserve - negative_target_eth_reserve
    )


def how_much_token_to_buy():
    pass


def get_current_reserves(exchange_addr=USDC_EXCHANGE_ADDR):
    conn = web3_infura.Connection()
    exchange = uniswap.Exchange(exchange_addr, conn)
    (eth_reserve, token_reserve) = calculate_pool(conn.w3, exchange.contract)
    return (eth_reserve, token_reserve)


def main():
    (eth_reserve, token_reserve) = get_current_reserves()
    exchange_rate = calculate_exchange_rate(eth_reserve, token_reserve)
    return exchange_rate


if __name__ == '__main__':
    # print(calculate_dataset())
    # print(main(DAI_EXCHANGE_ADDR))
    print(main())
    # print(main('0x4e395304655F0796bc3bc63709DB72173b9DdF98'))
