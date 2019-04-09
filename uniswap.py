import json
from pathlib import Path

DAI_EXCHANGE_ADDR = '0x09cabec1ead1c0ba254b09efb3ee13841712be14'
USDC_EXCHANGE_ADDR = '0x97deC872013f6B5fB443861090ad931542878126'

PROVIDER_FEE_PERCENT = 0.003
USDC_MARKET_CREATION_BLOCK = 7101817
USDC_TOKEN_DECIMALS = 6


class Exchange:
    def __init__(self, address, connection):
        self.conn = connection
        self.address = self.conn.w3.toChecksumAddress(address)
        json_path = Path(__file__).parent / 'exchangeABI.json'
        with json_path.open() as fp:
            self.abi = json.load(fp)

    @property
    def rate(self):
        """
        get current exchange rate per eth
        NOTE: this doesnt seem to work for usdc
        """
        return self.contract.functions.getEthToTokenInputPrice(1).call()

    @property
    def contract(self):
        return self.conn.w3.eth.contract(address=self.address, abi=self.abi)
