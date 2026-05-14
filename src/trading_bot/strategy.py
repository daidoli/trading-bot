from __future__ import annotations

import backtrader as bt  # type: ignore


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
