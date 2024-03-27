import requests
from os import getenv
from dotenv import load_dotenv
from constants import (
    COW_AMM_ADDRESS,
    COW_SETTLEMENT_CONTRACT,
    TOKEN1,
    TOKEN2,
    ORIGINAL_TOKEN2_TRANSFER,
    ORIGINAL_TOKEN1_TRANSFER,
    ORIGINAL_BLOCK,
    ORIGINAL_TIME,
    API_KEY,
    SCAN,
    END_BLOCK
)


def compute_cow_amm_trades():
    """
    To describe how the reserves of the AMM evolve over time, we will use a list, where each
    entry is dictionary {"TOKEN1": x, "TOKEN2": y, "block": b, "time": t}  which describes the ETH
    reserves (x) and the COW reserves (y) at the end of block b (meaning that the AMM traded at
    block b) and time t (timestamp in seconds).
    """

    AMM_states = []

    # INITIALIZATION
    AMM_states.append(
        {
            TOKEN1 : ORIGINAL_TOKEN1_TRANSFER,
            TOKEN2 : ORIGINAL_TOKEN2_TRANSFER,
            "block": ORIGINAL_BLOCK,
            "time": ORIGINAL_TIME,
        }
    )
    load_dotenv()
    SCAN_API_KEY = getenv(API_KEY)
    ### main loop going over all transfers

    start_block = ORIGINAL_BLOCK + 1
    i = 1
    while True:
        url = (
            "https://api."
            + SCAN
            +".io/api?module=account&action=tokentx&address="
            + COW_AMM_ADDRESS
            + "&startblock="
            + str(start_block)
            + "&endblock="
            + str(END_BLOCK)
            +"&sort=asc"
            + "&page="
            + str(i)
            + "&offset=1000&apikey="
            + SCAN_API_KEY
        )
        
        res = requests.get(url)

        if res.ok:
            resp = res.json()["result"]
            if len(resp) == 0:
                break
            k = len(resp)
            n = len(AMM_states)
            block_number = AMM_states[n - 1]["block"]
            new_state = AMM_states[n - 1]
            for j in range(k):
                a = resp[j]
                if block_number != int(a["blockNumber"]):
                    AMM_states.append(new_state)
                    block_number = int(a["blockNumber"])
                    new_state = {}
                    new_state["block"] = int(a["blockNumber"])
                    new_state["time"] = int(a["timeStamp"])
                    n+=1
                sign_a = 1
                if a["to"] == COW_SETTLEMENT_CONTRACT: 
                    sign_a = -1
                value = new_state.get(AMM_states[-1][a["tokenSymbol"]], 0)
                new_state[a["tokenSymbol"]] = value + sign_a * int(a["value"])
             

            #We're not considering the liquidity injection to the pool
            
        i = i + 1
    AMM_states.append(new_state)
    return AMM_states

from dataframes import states_to_df
print(states_to_df(compute_cow_amm_trades()))