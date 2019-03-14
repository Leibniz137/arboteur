Arbritrages USDC on UniSwap

# Algorithm
```
if the uniprice of eth is high (compared to oracle)

if the uniprice of eth is low (compared to oracle)
```

# Invariants
Trades are made only if there is more than 20$ profit

# Oracle
median of:
- uniswap dai price
- coinmarket cap: https://api.coinmarketcap.com/v1/ticker/ethereum/
- coinbase api
- etherscan: https://api.etherscan.io/api?module=stats&action=ethprice&apikey=YourApiKeyToken
