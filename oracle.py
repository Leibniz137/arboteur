import statistics

import requests

# hi tram!


def coinbase_price():
    url = 'https://api.coinbase.com/v2/exchange-rates?currency=eth'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['data']['rates']['USDC']


def etherscan_price():
    with open('./etherscan-api-token.txt') as fp:
        api_token = fp.read().strip()
    url = f'https://api.etherscan.io/api?module=stats&action=ethprice&apikey={api_token}'   # noqa: E501
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['result']['ethusd']


def coinmarketcap_price():
    url = 'https://api.coinmarketcap.com/v1/ticker/ethereum'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()[0]['price_usd']


def main():
    return statistics.median(
        map(float, [
            coinbase_price(),
            etherscan_price(),
            coinmarketcap_price()
        ])
    )


if __name__ == '__main__':
    print(main())
