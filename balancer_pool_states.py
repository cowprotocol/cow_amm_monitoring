import requests
from os import getenv
from dotenv import load_dotenv
from constants import (
    BALANCER_VAULT_CONTRACT,
    BALANCER_SWAP_TOPIC,
    BALANCER_POOL_TOPIC,
    BALANCER_PRICE_ORACLE_CONTRACT,
    TOKEN0_ADDRESS,
    TOKEN1_ADDRESS,
    TOKEN0_BALANCER,
    TOKEN1_BALANCER,
    TOKEN0,
    TOKEN1,
    START_BLOCK,
    END_BLOCK,
    API_KEY,
    CURRENT_TOKEN0,
    CURRENT_TOKEN1,
    CURRENT_TIME,
    SCAN
)


def twos_complement(hexstr, bits):
    value = int(hexstr, 16)
    if value & (1 << (bits - 1)):
        value -= 1 << bits
    return value


def compute_balancer_pool_liquidity_changes(SCAN_API_KEY):
    result = []
    i = 1

    while True:
        url = (
            "https://api."
            + SCAN
            +".io/api?module=logs&action=getLogs&fromBlock="
            + str(START_BLOCK)
            + "&toBlock="
            + str(END_BLOCK)
            +"&address="
            + BALANCER_VAULT_CONTRACT
            + "&topic0=0xe5ce249087ce04f05a957192435400fd97868dba0e6a4b4c049abf8af80dae78"
            +"&topic1="
            + BALANCER_POOL_TOPIC
            +"&page="
            + str(i)
            + "&offset=1000&apikey="
            + SCAN_API_KEY
        )
        
        res = requests.get(url)
        if res.ok:
            resp = res.json()["result"]
            if resp is None or len(resp) == 0:
                break
            for x in resp:
                block = int(x["blockNumber"], 16)
                time = int(x["timeStamp"], 16)
                data = x["data"][2:]
                token0 = "0x" + data[280:320]
                token0_delta = twos_complement("0x" + data[448:512], 256)
                token1_delta = twos_complement("0x" + data[512:576], 256)
                if int(token0,16) == int(TOKEN0_ADDRESS,16):
                    new_entry = {
                        "block": block,
                        TOKEN0: token0_delta,
                        TOKEN1: token1_delta,
                        "time": time,
                    }
                else:
                    new_entry = {
                        "block": block,
                        TOKEN0: token1_delta,
                        TOKEN1: token0_delta,
                        "time": time,
                    }
                result.append(new_entry)
        i = i + 1

    return result


########


def compute_balancer_pool_swaps(SCAN_API_KEY):
    ######### WE NOW ATTEMPT TO COMPUTE ALL THE REBALANCES OF THE BALANCER COW/WETH POOL
    i = 1
    result = []
    while True:
        url = (
            "https://api."
            + SCAN
            +".io/api?module=logs&action=getLogs&address="
            + BALANCER_VAULT_CONTRACT
            + "&topic0_1_opr=and"
            + "&topic1="
            + BALANCER_POOL_TOPIC
            + "&fromBlock="
            + str(START_BLOCK)
            + "&toBlock="
            + str(END_BLOCK)
            +"&page="
            + str(i)
            + "&offset=1000&apikey="
            + SCAN_API_KEY
        )
        res = requests.get(url)
        if res.ok:
            resp = res.json()["result"]
            if resp is None or len(resp) == 0:
                break
            for x in resp:
                if (
                    BALANCER_SWAP_TOPIC == x["topics"][0]
                    and BALANCER_PRICE_ORACLE_CONTRACT.lower() in x["topics"][1]
                ):
                    token_in = x["topics"][2].lower()
                    data = x["data"]
                    amount_in = int("0x" + data[2:66], 16)
                    amount_out = int("0x" + data[66:], 16)
                    block = int(x["blockNumber"], 16)
                    time = int(x["timeStamp"], 16)
                    if int(token_in,16) == int(TOKEN1_BALANCER,16):
                        entry = {
                            "hash": x["transactionHash"],
                            "block": block,
                            TOKEN0: (-1) * amount_out,
                            TOKEN1: amount_in,
                            "time": time,
                        }
                    else:
                        entry = {
                            "hash": x["transactionHash"],
                            "block": block,
                            TOKEN0: amount_in,
                            TOKEN1: (-1) * amount_out,
                            "time": time,
                        }
                    result.append(entry)
        i = i + 1

    return result


#########


## from json instances. State of pool at block 19255503.

#    "0xde8c195aa41c11a0c4787372defbbddaa31306d2": {
#      "kind": "WeightedProduct",
#      "reserves": {
#        "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": {
#          "balance": "227250112810783827603",
#          "weight": "0.5"
#        },
#        "0xdef1ca1fb7fbcdc777520aa7f396b4e015f497ab": {
#          "balance": "1475000268143578981182997",
#          "weight": "0.5"
#        }
#      },


def compute_balancer_pool_states(current_token0 = CURRENT_TOKEN0, current_token1 = CURRENT_TOKEN1):
    load_dotenv()
    SCAN_API_KEY = getenv(API_KEY)

    balancer_pool_swaps = compute_balancer_pool_swaps(SCAN_API_KEY)
    balancer_pool_liquidity_changes = compute_balancer_pool_liquidity_changes(
        SCAN_API_KEY
    )

    n = len(balancer_pool_swaps)
    m = len(balancer_pool_liquidity_changes)
    i = 0
    j = 0
    balancer_pool_states = []
    balancer_pool_states.append(
        {
            "block": START_BLOCK,
            TOKEN0: current_token0,
            TOKEN1: current_token1,
            "time": CURRENT_TIME,
        }
    )
    for t in range(n + m):
        if i >= n:
            for t in balancer_pool_liquidity_changes[j:]:
                current_token0 += t[TOKEN0]
                current_token1 += t[TOKEN1]
                balancer_pool_states.append(
                    {
                        "block": t["block"],
                        TOKEN0: current_token0,
                        TOKEN1: current_token1,
                        "time": t["time"],
                    }
                )
            break
        if j >= m:
            for t in balancer_pool_swaps[i:]:
                current_token0 += t[TOKEN0]
                current_token1 += t[TOKEN1]
                balancer_pool_states.append(
                    {
                        "block": t["block"],
                        TOKEN0: current_token0,
                        TOKEN1: current_token1,
                        "time": t["time"],
                    }
                )
            break
        if (
            balancer_pool_swaps[i]["block"]
            == balancer_pool_liquidity_changes[j]["block"]
        ):
            current_token0 += (
                balancer_pool_swaps[i][TOKEN0]
                + balancer_pool_liquidity_changes[j][TOKEN0]
            )
            current_token1 += (
                balancer_pool_swaps[i][TOKEN1]
                + balancer_pool_liquidity_changes[j][TOKEN1]
            )
            balancer_pool_states.append(
                {
                    "block": balancer_pool_swaps[i]["block"],
                    TOKEN0: current_token0,
                    TOKEN1: current_token1,
                    "time": balancer_pool_swaps[i]["time"],
                }
            )
            i = i + 1
            j = j + 1
        elif (
            balancer_pool_swaps[i]["block"]
            < balancer_pool_liquidity_changes[j]["block"]
        ):
            current_token0 += balancer_pool_swaps[i][TOKEN0]
            current_token1 += balancer_pool_swaps[i][TOKEN1]
            balancer_pool_states.append({
                    "block": balancer_pool_swaps[i]["block"],
                    TOKEN0: current_token0,
                    TOKEN1: current_token1,
                    "time": balancer_pool_swaps[i]["time"],
                })
            i = i + 1            
        else:
            current_token0 += balancer_pool_liquidity_changes[j][TOKEN0]
            current_token1 += balancer_pool_liquidity_changes[j][TOKEN1]
            balancer_pool_states.append(
                {
                    "block": balancer_pool_liquidity_changes[j]["block"],
                    TOKEN0: current_token0,
                    TOKEN1: current_token1,
                    "time": balancer_pool_liquidity_changes[j]["time"],
                }
            )
            j = j + 1       
    return balancer_pool_states

