from __future__ import annotations

import argparse
from pathlib import Path

import backtrader as bt  # type: ignore
import matplotlib
import pandas as pd  # type: ignore
import yfinance as yf  # type: ignore


def configure_matplotlib_fonts() -> None:
    matplotlib.rcParams["font.family"] = "sans-serif"
    matplotlib.rcParams["font.sans-serif"] = [
        "PingFang TC",
        "Heiti TC",
        "Arial Unicode MS",
        "Noto Sans CJK TC",
        "DejaVu Sans",
    ]
    matplotlib.rcParams["axes.unicode_minus"] = False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="動量交易策略回測")
    parser.add_argument(
        "--plot",
        action="store_true",
        help="回測完成後顯示圖表視窗",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="將圖表保存到文件（output/momentum_backtest_results.png），默認顯示交互式視窗",
    )
    parser.add_argument(
        "--refresh-cache",
        action="store_true",
        help="忽略本機快取並重新下載 BTC-USD 數據",
    )
    return parser.parse_args()


class Strategy(bt.Strategy):
    params = (("momentum_period", 20),)

    def __init__(self):
        momentum_period = self.params.momentum_period  # type: ignore
        # Calculate momentum: pt - pt-n
        self.momentum = self.data.close - self.data.close(-momentum_period)
        self.order = None
        self.daily_values = []

    def next(self):
        momentum_period = self.params.momentum_period  # type: ignore
        # Check if we have enough data
        if len(self) < momentum_period + 1:
            return

        # If we have an order pending, skip
        if self.order:
            return

        # If not in position
        if not self.position:
            if self.momentum[0] > 0:
                self.order = self.buy()
        else:
            if self.momentum[0] < 0:
                self.order = self.sell()

        self.daily_values.append(self.broker.getvalue())

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                print(f"買入已執行，價格: {order.executed.price:.2f}, " f"成本: {order.executed.value:.2f}, " f"手續費: {order.executed.comm:.2f}")
            else:
                print(f"賣出已執行，價格: {order.executed.price:.2f}, " f"成本: {order.executed.value:.2f}, " f"手續費: {order.executed.comm:.2f}")

        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            pnl_pct = (trade.pnl / (trade.barlen * trade.price)) * 100 if trade.price else 0
            print(f"交易已結束：利潤: {trade.pnl:.2f}, " f"利潤比例: {pnl_pct:.2f}%")


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


class Backtester:
    def __init__(
        self,
        args: argparse.Namespace,
        data_manager: DataManager,
    ) -> None:
        self._args = args
        self._data_manager = data_manager
        self._initial_value = 100000.0
        self._momentum_period = 30
        self._commission = 0.001

    def run(self) -> None:
        price_data = self._data_manager.load_price_data(refresh_cache=self._args.refresh_cache)
        cerebro = self._backtest(price_data)

        if self._args.plot:
            cerebro.plot()

    def _backtest(self, price_df: pd.DataFrame) -> bt.Cerebro:
        price_df.index.name = "datetime"
        price_pd = bt.feeds.PandasData(dataname=price_df)  # pyright: ignore[reportCallIssue]

        cerebro = bt.Cerebro()
        cerebro.addstrategy(Strategy, momentum_period=self._momentum_period)
        cerebro.adddata(price_pd)
        cerebro.broker.setcash(self._initial_value)
        cerebro.broker.setcommission(self._commission)
        cerebro.run()

        final_value = cerebro.broker.getvalue()
        returns = ((final_value - self._initial_value) / self._initial_value) * 100

        print(f"初始投資組合價值：{self._initial_value:.2f}")
        print(f"最終投資組合價值：{final_value:.2f}")
        print(f"總收益：{returns:.2f}%")

        return cerebro


if __name__ == "__main__":
    configure_matplotlib_fonts()
    args = parse_args()

    data_manager = DataManager()
    runner = Backtester(args, data_manager)
    runner.run()
