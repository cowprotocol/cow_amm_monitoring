"""Functions to process DataFrames"""

import polars as pl
import numpy as np


def states_to_df(states):
    return pl.DataFrame(
        {
            "block_number": [s["block"] for s in states],
            "time": [s["time"] for s in states],
            "WETH": [float(s["WETH"]) for s in states],
            "COW": [float(s["COW"]) for s in states]
            # "COW": [float(s["GNO"]) for s in states]
        }
    )


def prices_to_df(prices):
    return pl.DataFrame(
        {"time": [p["time"] for p in prices], "price": [p["price"] for p in prices]}
    )


def combine_with_prices(df_amm, df_weth_prices, df_cow_prices):
    df_amm_aggregate = df_amm.clone()
    # add prices
    df_amm_aggregate = (
        df_amm_aggregate.join(df_weth_prices, on="time", how="outer_coalesce")
        .rename({"price": "price_weth"})
        .sort("time")
    )
    df_amm_aggregate = (
        df_amm_aggregate.join(df_cow_prices, on="time", how="outer_coalesce")
        .rename({"price": "price_cow"})
        .sort("time")
    )
    df_amm_aggregate = df_amm_aggregate.sort("time").with_columns(
        pl.col("WETH").fill_null(strategy="forward")
    )
    df_amm_aggregate = df_amm_aggregate.sort("time").with_columns(
        pl.col("COW").fill_null(strategy="forward")
    )
    df_amm_aggregate = df_amm_aggregate.sort("time").with_columns(
        pl.col("price_weth").interpolate()
    )
    df_amm_aggregate = df_amm_aggregate.sort("time").with_columns(
        pl.col("price_cow").interpolate()
    )
    df_amm_aggregate = (
        df_amm_aggregate.filter(pl.col("WETH").is_not_null())
        .filter(pl.col("price_weth").is_not_null())
        .filter(pl.col("price_cow").is_not_null())
    )
    # compute values
    df_amm_aggregate = df_amm_aggregate.with_columns(
        (pl.col("WETH") / 10**18 * pl.col("price_weth")).alias("value_weth")
    )
    df_amm_aggregate = df_amm_aggregate.with_columns(
        (pl.col("COW") / 10**18 * pl.col("price_cow")).alias("value_cow")
    )
    df_amm_aggregate = df_amm_aggregate.with_columns(
        (pl.col("value_weth") + pl.col("value_cow")).alias("total_value")
    )
    df_amm_aggregate = df_amm_aggregate.with_columns(
        (pl.col("total_value").log().diff().exp()).alias("total_value_change")
    )
    # compute holding value
    df_amm_aggregate = df_amm_aggregate.with_columns(
        (pl.first("WETH") / 10**18 * pl.col("price_weth")).alias("holding_value_weth")
    )
    df_amm_aggregate = df_amm_aggregate.with_columns(
        (pl.first("COW") / 10**18 * pl.col("price_cow")).alias("holding_value_cow")
    )
    df_amm_aggregate = df_amm_aggregate.with_columns(
        (pl.col("holding_value_weth") + pl.col("holding_value_cow")).alias(
            "total_holding_value"
        )
    )
    df_amm_aggregate = df_amm_aggregate.with_columns(
        (pl.col("total_holding_value").log().diff().exp()).alias(
            "total_holding_value_change"
        )
    )
    # profit vs holding
    df_amm_aggregate = df_amm_aggregate.with_columns(
        (pl.col("total_value_change") / pl.col("total_holding_value_change")).alias(
            "profit_vs_holding_change"
        )
    )

    return df_amm_aggregate


def plot_profit_vs_holding(df):
    plt = (
        df.filter(
            ((pl.col("WETH").diff() == 0) & (pl.col("COW").diff() == 0))
            | (
                (pl.col("WETH").diff() != 0)
                & (pl.col("COW").diff() != 0)
                & (pl.col("WETH").diff() * pl.col("COW").diff() < 0)
            )
        )
        .with_columns(
            pl.col("profit_vs_holding_change")
            .cum_prod()
            .alias("profit_vs_holding_relative")
        )
        .with_columns(pl.from_epoch("time", time_unit="s").alias("time"))
        .plot(x="time", y="profit_vs_holding_relative")
    )

    return plt


def compute_profit_vs_holding_apy(df, correction=1):
    df_filtered = df.filter(~pl.col("total_value").is_null())
    start_time = df_filtered["time"][0]
    end_time = df_filtered["time"][-1]
    power = (60 * 60 * 24 * 365) / (end_time - start_time)
    # power = 1
    profit_vs_holding = (
        df_filtered.filter(
            ((pl.col("WETH").diff() == 0) & (pl.col("COW").diff() == 0))
            | (
                (pl.col("WETH").diff() != 0)
                & (pl.col("COW").diff() != 0)
                & (pl.col("WETH").diff() * pl.col("COW").diff() < 0)
            )
        ).with_columns(
            pl.col("profit_vs_holding_change")
            .cum_prod()
            .alias("profit_vs_holding_relative")
        )[
            "profit_vs_holding_relative"
        ][
            -1
        ]
        * correction
    ) ** power

    return profit_vs_holding
