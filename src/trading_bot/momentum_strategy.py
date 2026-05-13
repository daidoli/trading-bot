from __future__ import annotations

import argparse
from pathlib import Path

import backtrader as bt  # type: ignore
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd  # type: ignore
import yfinance as yf  # type: ignore
from matplotlib.ticker import FuncFormatter


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


class MomentumStrategy(bt.Strategy):
    params = (("momentum_period", 20),)

    def __init__(self):
        momentum_period = self.params.momentum_period  # type: ignore
        # Calculate momentum: pt - pt-n
        self.momentum = self.data.close - self.data.close(-momentum_period)
        self.order = None

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
            # Buy if momentum is positive (uptrend)
            if self.momentum[0] > 0:
                self.order = self.buy()
        else:
            # Sell if momentum is negative (downtrend)
            if self.momentum[0] < 0:
                self.order = self.sell()

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


class Runner:
    def run(self) -> None:
        parser = argparse.ArgumentParser(description="動量交易策略回測")
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
        args = parser.parse_args()

        price_data = self._load_price_data(refresh_cache=args.refresh_cache)
        price_data, returns = self._backtest(price_data)

        # Plot performance chart
        print("\n生成性能圖表...")
        self._plot_backtest_results(price_data, returns, save_to_file=args.save)

    def _backtest(self, price_df: pd.DataFrame) -> tuple[pd.DataFrame, float]:
        price_df.index.name = "datetime"
        price_pd = bt.feeds.PandasData(dataname=price_df)  # pyright: ignore[reportCallIssue]

        initial_value = 100000.0

        cerebro = bt.Cerebro()
        cerebro.addstrategy(MomentumStrategy, momentum_period=20)
        cerebro.adddata(price_pd)
        cerebro.broker.setcash(initial_value)
        cerebro.broker.setcommission(commission=0.001)
        cerebro.run()

        final_value = cerebro.broker.getvalue()
        returns = ((final_value - initial_value) / initial_value) * 100

        print(f"初始投資組合價值：{initial_value:.2f}")
        print(f"最終投資組合價值：{final_value:.2f}")
        print(f"總收益：{returns:.2f}%")

        return price_df, returns

    def _load_price_data(self, refresh_cache: bool = False) -> pd.DataFrame:
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

    def _plot_backtest_results(
        self,
        data_df: pd.DataFrame,
        returns: float,
        save_to_file: bool = False,
    ) -> None:
        if save_to_file:
            matplotlib.use("Agg")  # Use non-interactive backend for file output
            # Create output directory if it doesn't exist
            import os

            os.makedirs("output", exist_ok=True)
        else:
            # Use default interactive backend for display
            pass

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        # Plot 1: BTC Price
        ax1.plot(
            data_df.index,
            data_df["close"],
            label="BTC 收盤價",
            linewidth=2,
            color="blue",
        )
        ax1.set_ylabel("價格 (USD)", fontsize=12)
        ax1.set_title("BTC-USD 價格圖表 (2024-2025)", fontsize=14, fontweight="bold")
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc="upper left")

        # Plot 2: Portfolio value over time (simulated)
        dates = data_df.index
        daily_returns = data_df["close"].pct_change().fillna(0)
        cumulative_returns = (1 + daily_returns).cumprod()
        simulated_portfolio = 100000.0 * cumulative_returns * (returns / 100 + 1)

        ax2.plot(
            dates,
            simulated_portfolio,
            label="投資組合價值",
            linewidth=2,
            color="green",
        )
        ax2.fill_between(dates, 100000.0, simulated_portfolio, alpha=0.3, color="green")
        ax2.set_ylabel("投資組合價值 (USD)", fontsize=12)
        ax2.set_xlabel("日期", fontsize=12)
        ax2.set_title(f"投資組合表現 (總收益: {returns:.2f}%)", fontsize=14, fontweight="bold")
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc="upper left")

        # Format y-axis as currency
        ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"${x:,.0f}"))
        ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"${x:,.0f}"))

        plt.tight_layout()

        if save_to_file:
            # Save the plot to file
            output_path = "output/momentum_backtest_results.png"
            plt.savefig(output_path, dpi=150, bbox_inches="tight")
            print(f"圖表已保存到 {output_path}")
            plt.close()
        else:
            # Display the plot in interactive window
            print("顯示圖表視窗...")
            plt.show()


if __name__ == "__main__":
    configure_matplotlib_fonts()

    runner = Runner()
    runner.run()
