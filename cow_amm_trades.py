import requests
from os import getenv
from dotenv import load_dotenv
from constants import (
    COW_AMM_ADDRESS,
    COW_SETTLEMENT_CONTRACT,
    ORIGINAL_GNO_TRANSFER,
    ORIGINAL_WETH_TRANSFER,
    ORIGINAL_BLOCK,
    ORIGINAL_TIME,
    API_KEY,
    SCAN,
    END_BLOCK
)


def compute_cow_amm_trades():
    """
    To describe how the reserves of the AMM evolve over time, we will use a list, where each
    entry is dictionary {"WETH": x, "COW": y, "block": b, "time": t}  which describes the ETH
    reserves (x) and the COW reserves (y) at the end of block b (meaning that the AMM traded at
    block b) and time t (timestamp in seconds).
    """

    AMM_states = []

    # INITIALIZATION
    AMM_states.append(
        {
            "WETH": ORIGINAL_WETH_TRANSFER,
            "GNO": ORIGINAL_GNO_TRANSFER,
            "block": ORIGINAL_BLOCK,
            "time": ORIGINAL_TIME,
        }
    )
    load_dotenv()
    ETHERSCAN_API_KEY = getenv(API_KEY)
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
            + ETHERSCAN_API_KEY
        )
        
        res = requests.get(url)

        if res.ok:
            resp = res.json()["result"]
            if resp is None:
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
                sign_a = 1
                if a["to"] == COW_SETTLEMENT_CONTRACT: 
                    sign_a = -1
                value = new_state.get(a["tokenSymbol"], 0)
                new_state[a["tokenSymbol"]] = value + sign_a * int(a["value"])
            AMM_states.append(new_state) 



        """
            k = len(resp) // 2
            n = len(AMM_states)
            for i in range(k):
                new_state = {}
                a = resp[2 * i]
                b = resp[2 * i + 1]
                if a["blockNumber"] != b["blockNumber"]:
                    print("Problem!! Exiting")
                    exit(1)              
                new_state["block"] = int(a["blockNumber"])
                new_state["time"] = int(a["timeStamp"])
                sign_a = 1
                sign_b = 1
                if a["to"] == COW_SETTLEMENT_CONTRACT:
                    sign_a = -1
                if b["to"] == COW_SETTLEMENT_CONTRACT:
                    sign_b = -1
                new_state[a["tokenSymbol"]] = AMM_states[n - 1][
                    a["tokenSymbol"]
                ] + sign_a * int(a["value"])
                new_state[b["tokenSymbol"]] = AMM_states[n - 1][
                    b["tokenSymbol"]
                ] + sign_b * int(b["value"])

                # if sign_a == sign_b == 1:
                #    print(
                #        "\nLiquidity injection for the CoW AMM. The new state is: "
                #        + str(new_state)
                #        + "\n"
                #    )

                #### AT THIS POINT WE HAVE COMPUTED THE NEW STATE
                AMM_states.append(new_state)
                n = n + 1
                """
        i = i + 1
    return AMM_states

