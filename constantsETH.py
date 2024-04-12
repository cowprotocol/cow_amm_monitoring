COW_AMM_ADDRESS = "0xBEEf5aFE88eF73337e5070aB2855d37dBF5493A4" #same across chains
COW_SETTLEMENT_CONTRACT = "0x9008d19f58aabd9ed0d60971565aa8510560ab41" #same across chains
BALANCER_PRICE_ORACLE_CONTRACT = "0xde8C195Aa41C11a0c4787372deFBbDdAa31306D2" #specific to the chain
BALANCER_VAULT_CONTRACT = "0xBA12222222228d8Ba445958a75a0704d566BF2C8" #same

#it's better to keep token1 to ETH or WETH since it serves as a reference for prices
TOKEN1 = "WETH"
TOKEN2 = "COW"
TOKEN1_COINGECKO = "ethereum"
TOKEN2_COINGECKO = "cow-protocol"
TOKEN2_ADDRESS = "0xdef1ca1fb7fbcdc777520aa7f396b4e015f497ab"
TOKEN1_ADDRESS = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
#get this info from the balancer explorer
TOKEN1_BALANCER = "0x000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
TOKEN2_BALANCER = "0x000000000000000000000000def1ca1fb7fbcdc777520aa7f396b4e015f497ab"
BALANCER_SWAP_TOPIC = (
    "0x2170c741c41531aec20e7c107c24eecfdd15e69c9bb0a8dd37b1840b9e0b207b"
)

#go on the contract of the balancer_price_oracle and read the function getPoolId
BALANCER_POOL_TOPIC = "0xDE8C195AA41C11A0C4787372DEFBBDDAA31306D2000200000000000000000181"

#arbitrary, but greater than the current block
END_BLOCK = 22000000
#This value comes from the sql query : fee_query
PROTOCOL_FEE_WEI = 192533777180722430
#the block at which the anlysis begins
START_TIME = 1708691819
START_BLOCK = 19255503

# AMM
#look on etherscan the first transactions which initialized the pool and at what block
ORIGINAL_TOKEN2_TRANSFER = 117134930000000000000000
ORIGINAL_TOKEN1_TRANSFER = 18190000000000000000
ORIGINAL_BLOCK = 19226568
ORIGINAL_TIME = 1707871271

# Balancer
"""
To find the curent amount:
1- find the tx hahash of where you want to start the analysis
2 - get the auction id here : https://api.cow.fi/docs/#/default/get_api_v1_solver_competition_by_tx_hash__tx_hash_
3 - Replace the auction id in the link and find the state of the balancer pool
https://solver-instances.s3.eu-central-1.amazonaws.com/prod/mainnet/legacy/8458170.json"""
CURRENT_TOKEN2 = 1475000268143578981182997
CURRENT_TOKEN1 = 227250112810783827603
CURRENT_TIME = 1708222403


API_KEY = "ETHERSCAN_KEY"
SCAN = "etherscan"

DELAY = 10  # in seconds

# requests
REQUEST_TIMEOUT = 5
SUCCESS_CODE = 200
FAIL_CODE = 404

HEADER = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
}