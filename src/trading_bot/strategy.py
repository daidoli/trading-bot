from __future__ import annotations

import backtrader as bt  # type: ignore


class Strategy(bt.Strategy):
    params = (
        ("momentum_period", 20),
        ("zscore_period", 20),
        ("zscore_threshold", 3.0),
        ("macd_fast", 12),
        ("macd_slow", 26),
        ("macd_signal", 9),
        ("rsi_short_period", 6),
        ("rsi_long_period", 14),
        ("rsi_overbought", 75),
        ("rsi_oversold", 25),
    )

    def __init__(self):
        momentum_period = self.params.momentum_period  # type: ignore
        zscore_period = self.params.zscore_period  # type: ignore
        # Calculate momentum: pt - pt-n
        self.momentum = self.data.close - self.data.close(-momentum_period)
        self.close_sma = bt.indicators.SimpleMovingAverage(  # pyright: ignore[reportAttributeAccessIssue, reportCallIssue]
            self.data.close, period=zscore_period
        )
        self.close_std = bt.indicators.StandardDeviation(self.data.close, period=zscore_period)  # pyright: ignore[reportCallIssue]
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
        self.rsi_overbought_indicator = self.rsi_long > self.params.rsi_overbought  # type: ignore
        self.rsi_oversold_indicator = self.rsi_long < self.params.rsi_oversold  # type: ignore
        self.order = None
        self.daily_values = []

    def next(self):
        momentum_period = self.params.momentum_period  # type: ignore
        zscore_period = self.params.zscore_period  # type: ignore
        zscore_threshold = float(self.params.zscore_threshold)  # type: ignore
        rsi_short_period = self.params.rsi_short_period  # type: ignore
        rsi_long_period = self.params.rsi_long_period  # type: ignore
        rsi_overbought = float(self.params.rsi_overbought)  # type: ignore
        rsi_oversold = float(self.params.rsi_oversold)  # type: ignore
        # Check if we have enough data
        if len(self) < max(momentum_period + 1, zscore_period, rsi_short_period, rsi_long_period) + 1:
            return

        rsi_now = float(self.rsi_long[0])
        rsi_prev = float(self.rsi_long[-1])
        close_now = float(self.data.close[0])
        market_volume = float(self.data.volume[0])
        close_std_now = float(self.close_std[0])

        if close_std_now > 0:
            zscore = (close_now - float(self.close_sma[0])) / close_std_now
            if abs(zscore) > zscore_threshold:
                print(
                    f"[{self.data.datetime.date(0)}] Z-Score 超過閾值 {zscore_threshold:.1f}: {zscore:.2f}, "
                    f"價格: {close_now:.2f}, 市場總量: {market_volume:.6f}"
                )

        if rsi_prev <= rsi_overbought and self.rsi_overbought_indicator[0]:
            print(
                f"[{self.data.datetime.date(0)}] RSI 超過 {rsi_overbought:.0f}: {rsi_now:.2f}, "
                f"價格: {close_now:.2f}, 市場總量: {market_volume:.6f}"
            )
        elif rsi_prev >= rsi_oversold and self.rsi_oversold_indicator[0]:
            print(
                f"[{self.data.datetime.date(0)}] RSI 低於 {rsi_oversold:.0f}: {rsi_now:.2f}, " f"價格: {close_now:.2f}, 市場總量: {market_volume:.6f}"
            )

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
                print(
                    f"買入已執行，價格: {order.executed.price:.2f}, "
                    f"數量: {order.executed.size:.6f}, "
                    f"成本: {order.executed.value:.2f}, "
                    f"手續費: {order.executed.comm:.2f}"
                )
            else:
                print(
                    f"賣出已執行，價格: {order.executed.price:.2f}, "
                    f"數量: {order.executed.size:.6f}, "
                    f"成本: {order.executed.value:.2f}, "
                    f"手續費: {order.executed.comm:.2f}"
                )

        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            pnl_pct = (trade.pnl / (trade.barlen * trade.price)) * 100 if trade.price else 0
            print(f"交易已結束：利潤: {trade.pnl:.2f}, " f"利潤比例: {pnl_pct:.2f}%")
