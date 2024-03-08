import requests
from os import getenv
from dotenv import load_dotenv
from constants import (
    COW_AMM_MAINNET_ADDRESS,
    COW_SETTLEMENT_CONTRACT,
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
    original_cow_transfer = 117134930000000000000000
    original_weth_transfer = 18190000000000000000
    original_block = 19226568
    AMM_states.append(
        {
            "WETH": original_weth_transfer,
            "COW": original_cow_transfer,
            "block": original_block,
            "time": 1707871271,
        }
    )
    load_dotenv()
    ETHERSCAN_API_KEY = getenv("ETHERSCAN_KEY")
    ### main loop going over all transfers

    start_block = original_block + 1
    i = 1
    while True:
        url = (
            "https://api.etherscan.io/api?module=account&action=tokentx&address="
            + COW_AMM_MAINNET_ADDRESS
            + "&startblock="
            + str(start_block)
            + "&endblock=27025780&sort=asc"
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
        i = i + 1

    return AMM_states
