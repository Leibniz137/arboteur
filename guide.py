"""
Uses eth price as reported by oracle and uniswap price
together to determine if profitable arbitrage is profitable
"""
import logging

import oracle
import uniprice

logging.basicConfig(level=logging.INFO)

# Total transaction fees
# uniswap + coinbase + gas
UNISWAP_TRANSACTION_FEE = 0.003

COINBASE_SPREAD = 0.005

# assuming the total transaction amount > $200 to avoid flat fee
# see: https://support.coinbase.com/customer/en/portal/articles/2109597-coinbase-pricing-fees-disclosures   # noqa: E501
COINBASE_FEE = 0.0149

TRANSACTION_FEE = UNISWAP_TRANSACTION_FEE + COINBASE_SPREAD + COINBASE_FEE


def main():
    oracle_price = oracle.main()
    logging.info(f"oracle price: {oracle_price}")

    exchange_rate = uniprice.main()
    logging.info(f"uniswap price: {exchange_rate}")

    price_ratio = 1 - oracle_price / exchange_rate
    logging.info(f"price ratio: {price_ratio}")
    logging.info(f"predicted fees: {TRANSACTION_FEE}")

    # TODO: how much to buy or sell?
    if price_ratio > TRANSACTION_FEE:
        logging.info("eth is overvalued on uniswap: SELL!")
    elif price_ratio < -TRANSACTION_FEE:
        # TODO: is USDC actually worth > 1$ ?
        logging.info("eth is undervalued on uniswap: BUY!")
    else:
        logging.info("uniswap price is accurate: HODL!")


if __name__ == '__main__':
    main()
