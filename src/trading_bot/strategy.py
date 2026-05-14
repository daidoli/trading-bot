from __future__ import annotations

import backtrader as bt  # type: ignore


class Strategy(bt.Strategy):
    params = (
        ("momentum_period", 20),
        ("macd_fast", 12),
        ("macd_slow", 26),
        ("macd_signal", 9),
        ("rsi_short_period", 6),
        ("rsi_long_period", 14),
    )

    def __init__(self):
        momentum_period = self.params.momentum_period  # type: ignore
        # Calculate momentum: pt - pt-n
        self.momentum = self.data.close - self.data.close(-momentum_period)
        self.macd = bt.indicators.MACD(
            period_me1=self.params.macd_fast,  # type: ignore
            period_me2=self.params.macd_slow,  # type: ignore
            period_signal=self.params.macd_signal,  # type: ignore
        )
        self.rsi_short = bt.indicators.RSI(
            self.data.close,
            period=self.params.rsi_short_period,  # type: ignore
        )
        self.rsi_long = bt.indicators.RSI(
            self.data.close,
            period=self.params.rsi_long_period,  # type: ignore
        )
        self.rsi_crossover = bt.indicators.CrossOver(self.rsi_short, self.rsi_long)  # type: ignore
        self.order = None
        self.daily_values = []

    def next(self):
        momentum_period = self.params.momentum_period  # type: ignore
        rsi_short_period = self.params.rsi_short_period  # type: ignore
        rsi_long_period = self.params.rsi_long_period  # type: ignore
        # Check if we have enough data
        if len(self) < max(momentum_period + 1, rsi_short_period, rsi_long_period) + 1:
            return

        # If we have an order pending, skip
        if self.order:
            return

        # If not in position
        if not self.position:
            # 多策略共振買進：動能 + MACD + RSI 黃金交叉
            if self.momentum[0] > 0 and self.macd.macd[0] > self.macd.signal[0] and self.rsi_crossover[0] > 0:
                self.order = self.buy()
        else:
            # 多策略共振賣出：動能 + MACD + RSI 死亡交叉
            if self.momentum[0] < 0 and self.macd.macd[0] < self.macd.signal[0] and self.rsi_crossover[0] < 0:
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
