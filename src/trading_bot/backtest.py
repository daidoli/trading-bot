from __future__ import annotations

import argparse

import backtrader as bt  # type: ignore
import matplotlib
import pandas as pd  # type: ignore

from trading_bot.data_manager import DataManager
from trading_bot.strategy import Strategy


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
    parser = argparse.ArgumentParser(description="動量 + MACD 交易策略回測")
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
