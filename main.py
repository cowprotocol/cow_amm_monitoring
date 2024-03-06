from cow_amm_trades import compute_cow_amm_trades
from balancer_pool_states import compute_balancer_pool_states
from plots import plot_spot_price, plot_invariant_over_blocks
from coingecko import get_token_price_in_usd
from constants import COW_TOKEN_ADDRESS, WETH_TOKEN_ADDRESS
import matplotlib.pyplot as plt


def main():
    cow_amm_states = compute_cow_amm_trades()
    balancer_pool_states = compute_balancer_pool_states()

    # WE NOW HAVE THE DATA WE NEED TO START COMPUTING STATISTICS ON THEM
    plot_spot_price(cow_amm_states, balancer_pool_states)
    plot_invariant_over_blocks(cow_amm_states)

    n = len(cow_amm_states)
    m = len(balancer_pool_states)
    current_cow_price = get_token_price_in_usd(COW_TOKEN_ADDRESS)
    current_weth_price = get_token_price_in_usd(WETH_TOKEN_ADDRESS)

    current_cow_reserve_price = (
        cow_amm_states[n - 1]["COW"] / 10**18
    ) * current_cow_price
    current_weth_reserve_price = (
        cow_amm_states[n - 1]["WETH"] / 10**18
    ) * current_weth_price
    current_price_original_cow_reserve = (
        980531661670314078251973 * current_cow_price / 10**18
    )
    current_price_original_weth_reserve = (
        138355268321545712793 * current_weth_price / 10**18
    )
    print(
        "\nOriginal CoW-AMM reserves value in current USD prices (COW / WETH / TOTAL): "
        + str(current_price_original_cow_reserve)
        + ", "
        + str(current_price_original_weth_reserve)
        + ", "
        + str(current_price_original_cow_reserve + current_price_original_weth_reserve)
        + "\n"
    )
    print(
        "\nCurrent CoW-AMM reserves value in current USD prices (COW / WETH / TOTAL): "
        + str(current_cow_reserve_price)
        + ", "
        + str(current_weth_reserve_price)
        + ", "
        + str(current_cow_reserve_price + current_weth_reserve_price)
        + "\n"
    )
    print(
        "\nProfit so far: "
        + str(
            current_cow_reserve_price
            + current_weth_reserve_price
            - current_price_original_cow_reserve
            - current_price_original_weth_reserve
        )
    )
    print(
        "\nCurrent oracle spot price = "
        + str(balancer_pool_states[m - 1]["COW"] / balancer_pool_states[m - 1]["WETH"])
        + "\n"
    )
    plt.show()


if __name__ == "__main__":
    main()
