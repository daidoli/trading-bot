from __future__ import annotations

from pathlib import Path

import pandas as pd  # type: ignore
import yfinance as yf  # type: ignore


class DataManager:
    def load_price_data(self, refresh_cache: bool = False) -> pd.DataFrame:
        cache_dir = Path("output/cache")
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / "btc-usd_2024-01-01_2025-12-31_1d.csv"

        if cache_file.exists() and not refresh_cache:
            print(f"讀取本機快取：{cache_file}")
            cached_df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
            cached_df.index.name = "datetime"
            return cached_df

        print("從 yfinance 下載最新數據...")
        data_df = yf.download(
            "BTC-USD",
            start="2024-01-01",
            end="2025-12-31",
            interval="1d",
            auto_adjust=False,
            progress=False,
        )

        if data_df is None or data_df.empty:
            raise ValueError("未返回 BTC 價格數據。")

        if isinstance(data_df.columns, pd.MultiIndex):
            data_df.columns = [col[0] for col in data_df.columns]

        data_df.columns = [col.lower() for col in data_df.columns]
        data_df = data_df[["open", "high", "low", "close", "volume"]]
        data_df.index.name = "datetime"
        data_df.to_csv(cache_file)
        print(f"已寫入快取：{cache_file}")
        return data_df
