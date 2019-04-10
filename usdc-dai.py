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


def get_swaps(exchange, token_addr, csv_path, pickle_path):
    """
    get data on swapping the token of a given exchange for another token

    args:
      exchange: uniswap for input token
      token_addr: address of output token
      csv_path: path to etherscan transaction dataset for given exchange

    outputs pickled file at pickle_path
    """
    # dont use txhash as index (it is a number...)
    df = pd.read_csv(path, index_col=False)

    def get_tx(row):
        return exchange.conn.w3.eth.getTransaction(row['Txhash'])

    def get_input(row):
        return exchange.contract.decode_function_input(row['transaction'].input)   # noqa: E501

    df['transaction'] = df.apply(get_tx, axis=1)
    df['input'] = df.apply(get_input, axis=1)
    df['fn_name'] = df.apply(lambda x: x['input'][0].fn_name, axis=1)
    df['token_addr'] = df.apply(lambda x: x['input'][1].get('token_addr'), axis=1)   # noqa: E501

    def get_pickleable_input(row):
        """
        function type isn't serializable, so drop it

        input rows are (function, AttributeDict) 2-tuples
        """
        return exchange.contract.decode_function_input(row['transaction'].input)[1]   # noqa: E501

    usdc_to_dai_swaps = df.loc[df.token_addr == DAI_TOKEN_ADDR]
    usdc_to_dai_swaps['input'] = usdc_to_dai_swaps.apply(get_pickleable_input, axis=1)   # noqa: E501
    import pdb; pdb.set_trace()
    usdc_to_dai_swaps.to_pickle(pickle_path)


if __name__ == '__main__':
    conn = web3_infura.Connection()
    exchange = uniswap.Exchange(uniswap.USDC_EXCHANGE_ADDR, conn)
    events = exchange.contract.events
    init_block = uniswap.USDC_MARKET_CREATION_BLOCK

    thisdir = pathlib.Path(__file__).parent
    path = thisdir / 'export-0x97dec872013f6b5fb443861090ad931542878126-jan1st.csv'   # noqa: E501
    pickle_path = thisdir / 'usdc_to_dai_swaps.pickle'
    get_swaps(exchange, DAI_TOKEN_ADDR, path, pickle_path)
