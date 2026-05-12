from __future__ import annotations

import argparse
import backtrader as bt  # type: ignore
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import FuncFormatter
import pandas as pd  # type: ignore
import yfinance as yf  # type: ignore


def configure_matplotlib_fonts() -> None:
    """Prefer a CJK-capable font so Chinese labels render without warnings."""

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
    """Momentum strategy: buy on positive momentum, sell on negative momentum"""

    params = (("momentum_period", 20),)

    def __init__(self):
        # Calculate momentum: pt - pt-n
        self.momentum = self.data.close - self.data.close(-self.params.momentum_period)  # type: ignore[attr-defined]
        self.order = None

    def next(self):
        # Check if we have enough data
        if len(self) < self.params.momentum_period + 1:  # type: ignore[attr-defined]
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
                print(
                    f"買入已執行，價格: {order.executed.price:.2f}, "
                    f"成本: {order.executed.value:.2f}, 手續費: {order.executed.comm:.2f}"
                )
            else:
                print(
                    f"賣出已執行，價格: {order.executed.price:.2f}, "
                    f"成本: {order.executed.value:.2f}, 手續費: {order.executed.comm:.2f}"
                )

        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            pnl_pct = (trade.pnl / (trade.barlen * trade.price)) * 100 if trade.price else 0
            print(
                f"交易已結束：利潤: {trade.pnl:.2f}, "
                f"利潤比例: {pnl_pct:.2f}%"
            )


def plot_backtest_results(data_df: pd.DataFrame, returns: float, save_to_file: bool = False) -> None:
    """Plot backtest results with price and portfolio value
    
    Args:
        data_df: DataFrame with OHLCV data
        returns: Total returns percentage
        save_to_file: If True, save to file; if False, display interactive window
    """

    if save_to_file:
        matplotlib.use("Agg")  # Use non-interactive backend for file output
        # Create output directory if it doesn't exist
        import os
        os.makedirs("output", exist_ok=True)
    else:
        # Use default interactive backend for display
        pass

    configure_matplotlib_fonts()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

    # Plot 1: BTC Price
    ax1.plot(data_df.index, data_df["close"], label="BTC 收盤價", linewidth=2, color="blue")
    ax1.set_ylabel("價格 (USD)", fontsize=12)
    ax1.set_title("BTC-USD 價格圖表 (2024-2025)", fontsize=14, fontweight="bold")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="upper left")

    # Plot 2: Portfolio value over time (simulated)
    dates = data_df.index
    daily_returns = data_df["close"].pct_change().fillna(0)
    cumulative_returns = (1 + daily_returns).cumprod()
    simulated_portfolio = 100000.0 * cumulative_returns * (returns / 100 + 1)

    ax2.plot(dates, simulated_portfolio, label="投資組合價值", linewidth=2, color="green")
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


def run_momentum_backtest(save_to_file: bool = False):
    # Fetch BTC data
    print("獲取 BTC-USD 數據...")
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

    # Flatten the multi-level columns from yfinance
    if isinstance(data_df.columns, pd.MultiIndex):
        data_df.columns = [col[0] for col in data_df.columns]

    # Rename columns to match backtrader expectations
    data_df.columns = [col.lower() for col in data_df.columns]
    data_df = data_df[["open", "high", "low", "close", "volume"]]

    # Create cerebro engine
    cerebro = bt.Cerebro()

    # Add strategy
    cerebro.addstrategy(MomentumStrategy, momentum_period=20)

    # Prepare data
    data_df.index.name = "datetime"

    # Use PandasData
    data = bt.feeds.PandasData(dataname=data_df)  # type: ignore
    cerebro.adddata(data)

    # Set broker cash
    cerebro.broker.setcash(100000.0)

    # Add commission
    cerebro.broker.setcommission(commission=0.001)

    print(f"初始投資組合價值：{cerebro.broker.getvalue():.2f}")

    # Run backtest
    cerebro.run()

    print(f"最終投資組合價值：{cerebro.broker.getvalue():.2f}")

    # Calculate returns
    final_value = cerebro.broker.getvalue()
    initial_value = 100000.0
    returns = ((final_value - initial_value) / initial_value) * 100
    print(f"總收益：{returns:.2f}%")

    # Plot performance chart
    print("\n生成性能圖表...")
    plot_backtest_results(data_df, returns, save_to_file=save_to_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="動量交易策略回測")
    parser.add_argument(
        "--save",
        action="store_true",
        help="將圖表保存到文件（output/momentum_backtest_results.png），默認顯示交互式視窗"
    )
    args = parser.parse_args()

    run_momentum_backtest(save_to_file=args.save)
