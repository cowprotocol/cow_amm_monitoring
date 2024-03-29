from cow_amm_trades import compute_cow_amm_trades
from balancer_pool_states import compute_balancer_pool_states
from plots import plot_spot_price, plot_invariant_over_blocks
from coingecko import get_token_price_in_usd
from constants import (TOKEN2_ADDRESS, TOKEN1_ADDRESS, TOKEN1, TOKEN2, 
                       TOKEN1_COINGECKO, TOKEN2_COINGECKO, ORIGINAL_TOKEN2_TRANSFER, ORIGINAL_TOKEN1_TRANSFER)
import matplotlib.pyplot as plt


def main():

    """
    To describe how the reserves of an AMM evolve over time, we will use a list, where each
    entry is dictionary {"TOKEN1": x, "TOKEN2": y, "block": b, "time": t}  which describes the TOKEN1
    reserves (x) and the TOKEN2 reserves (y) at the end of block b (meaning that the AMM traded at
    block b) and time t (timestamp in seconds).

    The variables cow_amm_states and balancer_pool_states use this convention.
    """
    cow_amm_states = compute_cow_amm_trades()
    balancer_pool_states = compute_balancer_pool_states()

    # WE NOW HAVE THE DATA WE NEED TO START COMPUTING STATISTICS ON THEM
    plot_spot_price(cow_amm_states, balancer_pool_states)
    plot_invariant_over_blocks(cow_amm_states)

    n = len(cow_amm_states)
    m = len(balancer_pool_states)
    current_token2_price = get_token_price_in_usd(TOKEN2_COINGECKO)
    current_token1_price = get_token_price_in_usd(TOKEN1_COINGECKO)

    current_token2_reserve_price = (
        cow_amm_states[n - 1][TOKEN2] / 10**18
    ) * current_token2_price
    current_token1_reserve_price = (
        cow_amm_states[n - 1][TOKEN1] / 10**18
    ) * current_token1_price
    current_price_original_token2_reserve = (
        ORIGINAL_TOKEN2_TRANSFER * current_token2_price / 10**18
    )
    current_price_original_token1_reserve = (
        ORIGINAL_TOKEN1_TRANSFER * current_token1_price / 10**18
    )
    print(
        "\nOriginal CoW-AMM reserves value in current USD prices ("+TOKEN2+" / "+TOKEN1+" / TOTAL): "
        + str(current_price_original_token2_reserve)
        + ", "
        + str(current_price_original_token1_reserve)
        + ", "
        + str(current_price_original_token2_reserve + current_price_original_token1_reserve)
        + "\n"
    )
    print(
        "\nCurrent CoW-AMM reserves value in current USD prices ("+TOKEN2+" / "+TOKEN1+" / TOTAL): "
        + str(current_token2_reserve_price)
        + ", "
        + str(current_token1_reserve_price)
        + ", "
        + str(current_token2_reserve_price + current_token1_reserve_price)
        + "\n"
    )
    print(
        "\nProfit so far: "
        + str(
            current_token2_reserve_price
            + current_token1_reserve_price
            - current_price_original_token2_reserve
            - current_price_original_token1_reserve
        )
        + " USD"
    )
    print(
        "\nCurrent oracle spot price = "
        + str(balancer_pool_states[m - 1][TOKEN2] / balancer_pool_states[m - 1][TOKEN1])
        + "\n"
    )
    plt.show()


if __name__ == "__main__":
    main()
