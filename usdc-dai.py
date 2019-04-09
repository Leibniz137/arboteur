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
import web3_infura
import uniswap

if __name__ == '__main__':
    conn = web3_infura.Connection()
    exchange = uniswap.Exchange(uniswap.USDC_EXCHANGE_ADDR, conn)
    events = exchange.contract.events
    init_block = uniswap.USDC_MARKET_CREATION_BLOCK
    import pdb; pdb.set_trace()
    # for event in events.tokenToTokenSwapOutput(fromBlock=init_block):
    #     print(event)
