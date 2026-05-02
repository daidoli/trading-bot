from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd  # type: ignore
import yfinance as yf  # type: ignore


def fetch_2025_btc_prices() -> pd.DataFrame:
    data = yf.download(
        "BTC-USD",
        start="2025-01-01",
        end="2026-01-01",
        interval="1d",
        auto_adjust=False,
        progress=False,
    )
    if data is None or data.empty:
        raise ValueError("No BTC price data returned for 2025.")
    return data


def plot_prices(data: pd.DataFrame) -> None:
    if data.empty:
        raise ValueError("No BTC price data returned for 2025.")

    close = data["Close"].dropna()

    plt.figure(figsize=(12, 6))
    plt.plot(close.index.values, close.values, linewidth=1.5)  # type: ignore
    plt.title("BTC-USD Price in 2025")
    plt.xlabel("Date")
    plt.ylabel("Close Price (USD)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def main() -> None:
    prices = fetch_2025_btc_prices()
    plot_prices(prices)

if __name__ == "__main__":
    main()
