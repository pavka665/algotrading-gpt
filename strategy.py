import pandas as pd 
import numpy as np 
import plotly.graph_objects as go


class Strategy:
    def __init__(self, df, initial_budget, window=20, no_of_std=2, ema_period=50):
        self.df = df
        self.initial_budget = initial_budget
        self.current_budget = initial_budget
        self.window = window
        self.no_of_std = no_of_std
        self.ema_period = ema_period
        self.position = 0
        self.trades = []
        self._calculate_indicator()

    def _calculate_indicator(self):
        self.df['ema50'] = self.df['Close'].ewm(span=50, adjust=False).mean()

    def generate_signals(self):
        signals = []
        for i in range(1, len(self.df)):
            if self.df['Close'][i] > self.df['ema50'][i] and self.df['Close'][i-1] < self.df['ema50'][i-1]:
                signals.append((self.df['Open Time'][i], 1))
            elif self.df['Close'][i] < self.df['ema50'][i] and self.df['Close'][i-1] > self.df['ema50'][i-1]:
                signals.append((self.df['Open Time'][i], -1))
        return signals

    def run_backtest(self):
        signals = self.generate_signals()
        for date, signal in signals:
            price = self.df.loc[self.df['Open Time'] == date, 'Close'].values[0]
            if signal == 1 and self.position == 0:
                self.position = self.current_budget / price
                self.current_budget = 0
                self.trades.append((date, 'buy', price))
            elif signal == -1 and self.position > 0:
                self.current_budget = self.position * price
                self.position = 0
                self.trades.append((date, 'sell', price))

    def calculate_statistics(self):
        total_trades = len(self.trades) // 2
        profit_trades = 0
        loss_trades = 0
        total_profit = 0
        total_loss = 0

        for i in range(0, len(self.trades), 2):
            buy_price = self.trades[i][2]
            sell_price = self.trades[i+1][2]
            if sell_price > buy_price:
                 profit_trades += 1
                 total_profit += sell_price - buy_price
            else:
                loss_trades += 1
                total_loss += buy_price - sell_price

        stats = {
            'Total Trades': total_trades,
            'Profit Trades': profit_trades,
            'Loss Trades': loss_trades,
            'Total Profit': total_profit,
            'Total Loss': total_loss,
            'Net Profit': total_profit - total_loss,
            'Final Budget': self.current_budget if self.position == 0 else self.position * self.df['Close'].iloc[-1]
        }

        return stats