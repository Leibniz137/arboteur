"""
public contract methods

swap:
- tokenToTokenSwapInput
- tokenToTokenSwapOutput

transfer:
- tokenToTokenTransferInput
- tokenToTokenTransferOutput

assumption: we don't need to consider private contract methods
"""
import pathlib

import pandas as pd

import web3_infura
import uniswap

# LATEST_BLOCK = 7535973
LATEST_BLOCK = 7200000
PROVIDER_URI = 'https://mainnet.infura.io'
DAI_TOKEN_ADDR = '0x89d24A6b4CcB1B6fAA2625fE562bDD9a23260359'


def extract_input(exchange, txhash):
    tx = exchange.conn.w3.eth.getTransaction(txhash)
    input_ = exchange.contract.decode_function_input(tx.input)
    return input_


if __name__ == '__main__':
    conn = web3_infura.Connection()
    exchange = uniswap.Exchange(uniswap.USDC_EXCHANGE_ADDR, conn)
    events = exchange.contract.events
    init_block = uniswap.USDC_MARKET_CREATION_BLOCK

    records_path = pathlib.Path(__file__).parent / 'export-0x97dec872013f6b5fb443861090ad931542878126-jan1st.csv'   # noqa: E501
    records = pd.read_csv(records_path)
    inputs = [extract_input(exchange, txhash) for txhash in records.Txhash.to_dict()]   # noqa: E501
    token_to_token_transfers = [
        input_ for input_ in inputs if input_[0].fn_name.startswith('tokenToToken')   # noqa: E501
    ]
    dai_swaps = [input_ for input_ in token_to_token_transfers if input_[1]['token_addr'] == DAI_TOKEN_ADDR]   # noqa: E501
    import pdb; pdb.set_trace()

    # for event in events.tokenToTokenSwapOutput(fromBlock=init_block):
    #     print(event)
