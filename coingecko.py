import requests
from constants import HEADER, REQUEST_TIMEOUT
from typing import Optional


def get_token_price_in_usd(address: str) -> Optional[float]:
    """
    Returns the Coingecko price in usd of the given token.
    """
    coingecko_url = (
        "https://api.coingecko.com/api/v3/simple/token_price/ethereum?contract_addresses="
        + address
        + "&vs_currencies=usd"
    )
    try:
        coingecko_data = requests.get(
            coingecko_url,
            headers=HEADER,
            timeout=REQUEST_TIMEOUT,
        )
        coingecko_rsp = coingecko_data.json()
        coingecko_price_in_usd = float(coingecko_rsp[address]["usd"])
    except requests.RequestException as err:
        print("Failed to fetch price")
        return None
    return coingecko_price_in_usd


def get_historical_token_price(
    token_id: str, currency: str = "usd"
) -> list[list[float]]:
    """
    Returns the hourly historic Coingecko price in usd of the given token by id.
    COW is "cow-protocol", WETH is "ethereum"
    """
    coingecko_url = (
        "https://api.coingecko.com/api/v3/coins/"
        + token_id
        + "/market_chart?vs_currency="
        + currency
        + "&days=14"
    )
    try:
        coingecko_data = requests.get(
            coingecko_url,
            timeout=REQUEST_TIMEOUT,
        )
        coingecko_rsp = coingecko_data.json()
        prices = [
            {"time": int(p[0] / 1000), "price": p[1]} for p in coingecko_rsp["prices"]
        ]
    except requests.RequestException as err:
        print("Failed to fetch price")
        raise error
    return prices
