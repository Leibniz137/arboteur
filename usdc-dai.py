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

# TODO: additionally scan for dai -> usdc swaps (fiat offramp?)

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

    path = pathlib.Path(__file__).parent / 'export-0x97dec872013f6b5fb443861090ad931542878126-jan1st.csv'   # noqa: E501

    # dont use txhash as index (it is a number...)
    df = pd.read_csv(path, index_col=False)

    def get_tx(row):
        return exchange.conn.w3.eth.getTransaction(row['Txhash'])
    df['transaction'] = df.apply(get_tx, axis=1)
    df['input'] = df.apply(lambda x: exchange.contract.decode_function_input(x['transaction'].input), axis=1)   # noqa: E501
    df['fn_name'] = df.apply(lambda x: x['input'][0].fn_name, axis=1)
    df['token_addr'] = df.apply(lambda x: x['input'][1]['token_addr'], axis=1)

    # uniswap uscd to dai
    dai_swaps = df.loc[df.token_addr == DAI_TOKEN_ADDR]
    import pdb; pdb.set_trace()
