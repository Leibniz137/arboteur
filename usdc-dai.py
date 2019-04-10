"""
public contract methods

swap:
- tokenToTokenSwapInput
- tokenToTokenSwapOutput

transfer:
- tokenToTokenTransferInput
- tokenToTokenTransferOutput

assumption: we don't need to consider private contract methods


TODO:
usdc-dai.py:64: SettingWithCopyWarning:
A value is trying to be set on a copy of a slice from a DataFrame.
Try using .loc[row_indexer,col_indexer] = value instead

See the caveats in the documentation: http://pandas.pydata.org/pandas-docs/stable/indexing.html#indexing-view-versus-copy
  swaps['input'] = swaps.apply(get_pickleable_input, axis=1)
Traceback (most recent call last):
  File "usdc-dai.py", line 91, in <module>
    dai_exchange_output_pickle)
  File "usdc-dai.py", line 51, in get_swaps
    df['input'] = df.apply(get_input, axis=1)
  File "/Users/nathaniel/.virtualenvs/arboteur/lib/python3.7/site-packages/pandas/core/frame.py", line 6487, in apply
    return op.get_result()
  File "/Users/nathaniel/.virtualenvs/arboteur/lib/python3.7/site-packages/pandas/core/apply.py", line 151, in get_result
    return self.apply_standard()
  File "/Users/nathaniel/.virtualenvs/arboteur/lib/python3.7/site-packages/pandas/core/apply.py", line 257, in apply_standard
    self.apply_series_generator()
  File "/Users/nathaniel/.virtualenvs/arboteur/lib/python3.7/site-packages/pandas/core/apply.py", line 286, in apply_series_generator
    results[i] = self.f(v)
  File "usdc-dai.py", line 48, in get_input
    return exchange.contract.decode_function_input(row['transaction'].input)   # noqa: E501
  File "/Users/nathaniel/.virtualenvs/arboteur/lib/python3.7/site-packages/web3/utils/decorators.py", line 14, in _wrapper
    return self.method(obj, *args, **kwargs)
  File "/Users/nathaniel/.virtualenvs/arboteur/lib/python3.7/site-packages/web3/contract.py", line 692, in decode_function_input
    func = self.get_function_by_selector(selector)
  File "/Users/nathaniel/.virtualenvs/arboteur/lib/python3.7/site-packages/web3/utils/decorators.py", line 14, in _wrapper
    return self.method(obj, *args, **kwargs)
  File "/Users/nathaniel/.virtualenvs/arboteur/lib/python3.7/site-packages/web3/contract.py", line 686, in get_function_by_selector
    return get_function_by_identifier(fns, 'selector')
  File "/Users/nathaniel/.virtualenvs/arboteur/lib/python3.7/site-packages/web3/contract.py", line 1541, in get_function_by_identifier
    'Could not find any function with matching {0}'.format(identifier)
ValueError: ('Could not find any function with matching selector', 'occurred at index 2568')
"""
import pathlib

import pandas as pd
import web3

import web3_infura
import uniswap

# TODO: additionally scan for dai -> usdc swaps (fiat offramp?)

# LATEST_BLOCK = 7535973
LATEST_BLOCK = 7200000
PROVIDER_URI = 'https://mainnet.infura.io'
DAI_TOKEN_ADDR = '0x89d24A6b4CcB1B6fAA2625fE562bDD9a23260359'
USDC_TOKEN_ADDR = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'


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
    df = pd.read_csv(csv_path, index_col=False)

    def get_tx(row):
        return exchange.conn.w3.eth.getTransaction(row['Txhash'])

    def get_input(row):
        try:
            return exchange.contract.decode_function_input(row['transaction'].input)   # noqa: E501
        except Exception as e:
            print(e)
            return (web3.contract.ContractFunction(), {})

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

    swaps = df.loc[df.token_addr == token_addr]
    swaps['input'] = swaps.apply(get_pickleable_input, axis=1)
    swaps.to_pickle(pickle_path)


if __name__ == '__main__':
    conn = web3_infura.Connection()
    usdc_exchange = uniswap.Exchange(uniswap.USDC_EXCHANGE_ADDR, conn)
    dai_exchange = uniswap.Exchange(uniswap.DAI_EXCHANGE_ADDR, conn)

    thisdir = pathlib.Path(__file__).parent
    usdc_exchange_csv = thisdir / f'export-{uniswap.USDC_EXCHANGE_ADDR}-jan1st.csv'   # noqa: E501
    usdc_exchange_output_pickle = thisdir / 'usdc_to_dai_swaps.pickle'

    # NOTE: dai exchange data only goes to feb22 due to higher volume
    dai_exchange_csv = thisdir / f'export-{uniswap.DAI_EXCHANGE_ADDR}-jan1st.csv'   # noqa: E501
    dai_exchange_output_pickle = thisdir / 'dai_to_usdc_swaps.pickle'

    get_swaps(
        usdc_exchange,
        DAI_TOKEN_ADDR,
        usdc_exchange_csv,
        usdc_exchange_output_pickle)

    get_swaps(
        dai_exchange,
        USDC_TOKEN_ADDR,
        dai_exchange_csv,
        dai_exchange_output_pickle)
