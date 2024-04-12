#it's better to keep TOKEN0 to the wrapped native token of the chain (e.g. WETH for ethereum and wxDAI for gnosis chain) since it serves as a reference for prices

COW_AMM_ADDRESS = "0xb3861b445F873AeE9a5a4e1E2957d679Bc91B9E2" #GNO
COW_SETTLEMENT_CONTRACT = "0x9008d19f58aabd9ed0d60971565aa8510560ab41" #Same
BALANCER_PRICE_ORACLE_CONTRACT = "0xB8bB1ce9C6E5401D66fE2126dB6E7387E1E24fFE" #GNO
BALANCER_VAULT_CONTRACT = "0xBA12222222228d8Ba445958a75a0704d566BF2C8" #Same

TOKEN0 ='WETH'
TOKEN1 = 'GNO'
TOKEN0_COINGECKO = "ethereum"
TOKEN1_COINGECKO = "gnosis"
TOKEN0_ADDRESS = "0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1" #GNO
TOKEN1_ADDRESS = "0x9C58BAcC331c9aa871AFD802DB6379a98e80CEdb" #GNO

#The token adress with 24 bits before (0)
TOKEN0_BALANCER = "0x0000000000000000000000006A023CCd1ff6F2045C3309768eAd9E68F978f6e1" #to be found on balancer explorer
TOKEN1_BALANCER = "0x0000000000000000000000009C58BAcC331c9aa871AFD802DB6379a98e80CEdb" #to be found on balancer explorer

BALANCER_SWAP_TOPIC = (
    "0x2170c741c41531aec20e7c107c24eecfdd15e69c9bb0a8dd37b1840b9e0b207b"
) #Same #the signature of a balancer swap event
BALANCER_POOL_TOPIC = "0xb8bb1ce9c6e5401d66fe2126db6e7387e1e24ffe00020000000000000000003d"

END_BLOCK = 35000000

#AMM
#find the start information at the first transaction to create the am
START_BLOCK = 32236569 #GNO contract creation
START_TIME = 1706792110 #"2024-02-01 13:55:10" 
#adapt the query fee_query.sql to the chain (can be omitted for gnosis)
PROTOCOL_FEE_WEI = 0


# AMM
#to be found at the first transaction to create the amm
ORIGINAL_TOKEN1_TRANSFER = 10704795325587563812 #GNO : GNO
ORIGINAL_TOKEN0_TRANSFER = 2500000000000000000 #GNO : WETH
ORIGINAL_BLOCK = 32319424 #GNO contract creation
ORIGINAL_TIME = 1707235655 #"2024-02-06 16:07:35"

# Balancer
#Use the first transaction with CoW AMM, find the related auction_id
#Then use the auction_id to find Balancer's related balance
CURRENT_TOKEN1 = 20142939229994179615 #GNO on GNO
CURRENT_TOKEN0 = 2274141194013377880 #WETH on GNO
CURRENT_TIME = 1708925205 #2024-02-26 05:26:45

API_KEY = "GNOSISSCAN_KEY"
SCAN = "gnosisscan"



DELAY = 10  # in seconds

# requests
REQUEST_TIMEOUT = 5
SUCCESS_CODE = 200
FAIL_CODE = 404

HEADER = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
}