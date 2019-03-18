"""
NOTE: requires Infura api key

$ export WEB3_INFURA_API_KEY='...'
"""
from web3 import Web3


DAI_EXCHANGE_ADDR = '0x09cabec1ead1c0ba254b09efb3ee13841712be14'
FACTORY = '0xc0a47dFe034B400B47bDaD5FecDa2621de6c4d95'

PROJECT_ID = '029890c5690243edbcb9fc201eb85164'
PROVIDER_URL = f'https://mainnet.infura.io/v3/{PROJECT_ID}'


def main():
    provider = Web3.HTTPProvider(PROVIDER_URL)
    w3 = Web3(provider)
    assert w3.isConnected()

    address = w3.toChecksumAddress(DAI_EXCHANGE_ADDR)
    dai_swap = w3.eth.contract(address=address)
    return dai_swap


if __name__ == '__main__':
    print(main())
