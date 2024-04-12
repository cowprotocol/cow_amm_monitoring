"""Functions to process DataFrames"""

import polars as pl
import numpy as np
from constants import (
    TOKEN0,
    TOKEN1
)


def states_to_df(states):
    return pl.DataFrame(
        {
            "block_number": [s["block"] for s in states],
            "time": [s["time"] for s in states],
            TOKEN0: [float(s[TOKEN0]) for s in states],
            TOKEN1: [float(s[TOKEN1]) for s in states]
        }
    )


def prices_to_df(prices):
    return pl.DataFrame(
        {"time": [p["time"] for p in prices], "price": [p["price"] for p in prices]}
    )


def combine_with_prices(df_amm, df_token0_prices, df_token1_prices):
    df_amm_aggregate = df_amm.clone()
    # add prices
    df_amm_aggregate = (
        df_amm_aggregate.join(df_token0_prices, on="time", how="outer_coalesce")
        .rename({"price": "price_"+TOKEN0})
        .sort("time")
    )
    df_amm_aggregate = (
        df_amm_aggregate.join(df_token1_prices, on="time", how="outer_coalesce")
        .rename({"price": "price_"+TOKEN1})
        .sort("time")
    )
    df_amm_aggregate = df_amm_aggregate.sort("time").with_columns(
        pl.col(TOKEN0).fill_null(strategy="forward")
    )
    df_amm_aggregate = df_amm_aggregate.sort("time").with_columns(
        pl.col(TOKEN1).fill_null(strategy="forward")
    )
    df_amm_aggregate = df_amm_aggregate.sort("time").with_columns(
        pl.col("price_"+TOKEN0).interpolate()
    )
    df_amm_aggregate = df_amm_aggregate.sort("time").with_columns(
        pl.col("price_"+TOKEN1).interpolate()
    )
    df_amm_aggregate = (
        df_amm_aggregate.filter(pl.col(TOKEN0).is_not_null())
        .filter(pl.col("price_"+TOKEN0).is_not_null())
        .filter(pl.col("price_"+TOKEN1).is_not_null())
    )
    # compute values
    df_amm_aggregate = df_amm_aggregate.with_columns(
        (pl.col(TOKEN0) / 10**18 * pl.col("price_"+TOKEN0)).alias("value_"+TOKEN0)
    )
    df_amm_aggregate = df_amm_aggregate.with_columns(
        (pl.col(TOKEN1) / 10**18 * pl.col("price_"+TOKEN1)).alias("value_"+TOKEN1)
    )
    df_amm_aggregate = df_amm_aggregate.with_columns(
        (pl.col("value_"+TOKEN0) + pl.col("value_"+TOKEN1)).alias("total_value")
    )
    df_amm_aggregate = df_amm_aggregate.with_columns(
        (pl.col("total_value").log().diff().exp()).alias("total_value_change")
    )
    # compute holding value
    df_amm_aggregate = df_amm_aggregate.with_columns(
        (pl.first(TOKEN0) / 10**18 * pl.col("price_"+TOKEN0)).alias("holding_value_"+TOKEN0)
    )
    df_amm_aggregate = df_amm_aggregate.with_columns(
        (pl.first(TOKEN1) / 10**18 * pl.col("price_"+TOKEN1)).alias("holding_value_"+TOKEN1)
    )
    df_amm_aggregate = df_amm_aggregate.with_columns(
        (pl.col("holding_value_"+TOKEN0) + pl.col("holding_value_"+TOKEN1)).alias(
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
        df.filter(~(pl.col("total_value_change").log().abs() > 0.02))
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
        df_filtered.with_columns(
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
