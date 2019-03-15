import requests


def coinbase_price():
    response = requests.get('https://api.coinbase.com/v2/')
    response.raise_for_status()
    return response

def etherscan_price():
    pass


def main():
    print(coinbase_price())

if __name__ == '__main__':
  main()
