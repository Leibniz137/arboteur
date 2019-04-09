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
import shlex
import subprocess
import tempfile

import pandas as pd

import web3_infura
import uniswap

# LATEST_BLOCK = 7535973
LATEST_BLOCK = 7200000
PROVIDER_URI = 'https://mainnet.infura.io'

if __name__ == '__main__':
    conn = web3_infura.Connection()
    exchange = uniswap.Exchange(uniswap.USDC_EXCHANGE_ADDR, conn)
    events = exchange.contract.events
    init_block = uniswap.USDC_MARKET_CREATION_BLOCK
    cmd = shlex.split(
        "ethereumetl export_blocks_and_transactions"
        f" --start-block {uniswap.USDC_MARKET_CREATION_BLOCK}"
        f" --end-block {LATEST_BLOCK}"
        f" --provider-uri {PROVIDER_URI}"
        " --transactions-output -"
    )

    completed_proc = subprocess.run(
        cmd,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        # check=True,
    )
    with tempfile.TemporaryFile() as fp:
        fp.write(completed_proc.stdout)
        fp.seek(0)
        df = pd.read_csv(fp)
    txs = df.loc[(df['to_address'] == uniswap.USDC_EXCHANGE_ADDR) | (df['from_address'] == uniswap.USDC_EXCHANGE_ADDR)]   # noqa: E501
    import pdb; pdb.set_trace()

    # for event in events.tokenToTokenSwapOutput(fromBlock=init_block):
    #     print(event)
