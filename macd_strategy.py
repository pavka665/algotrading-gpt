import pandas as pd 
import numpy as np 
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from binance import Binance

class MACDStrategy:
    def __init__(self, df, long_ema=50, short_ema=30, macd_slow=26, macd_fast=3, macd_smooth=9):
        self.df = df
        self.macd_slow = macd_slow
        self.macd_fast = macd_fast
        self.macd_smooth = macd_smooth
        self.backcandles = 5

        self.df['ema_50'] = self.df['Close'].ewm(span=long_ema, adjust=False).mean()
        self.df['ema_30'] = self.df['Close'].ewm(span=short_ema, adjust=False).mean()
        self.df['macd'], self.df['signal_line'], self.df['hist'] = self.calculate_macd(self.df['Close'])

    def calculate_macd(self, price):
        ema_fast = price.ewm(span=self.macd_fast, adjust=False).mean()
        ema_slow = price.ewm(span=self.macd_slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=self.macd_smooth, adjust=False).mean()
        return macd, signal_line, macd - signal_line

    def run(self):
        self.df['signal'] = 0

        for i in range(1, len(self.df)):
            if self.df['macd'][i] > self.df['signal_line'][i] and self.df['macd'][i-1] < self.df['signal_line'][i-1]:
                if all(self.df['ema_30'][i-j] > self.df['ema_50'][i-j] for j in range(self.backcandles)):
                    self.df.at[i, 'signal'] = 1
            
            if self.df['macd'][i] < self.df['signal_line'][i] and self.df['macd'][i-1] > self.df['signal_line'][i-1]:
                if all(self.df['ema_30'][i-j] < self.df['ema_50'][i-j] for j in range(self.backcandles)):
                    self.df.at[i, 'signal'] = -1

        return self.df

    def plot(self):
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1, subplot_titles=('Price Chart', 'MACD'),
                            row_heights=[0.7, 0.3])

        # Candlestick chart
        fig.add_trace(go.Candlestick(x=self.df.index,
                                    open=self.df['Open'],
                                    high=self.df['High'],
                                    low=self.df['Low'],
                                    close=self.df['Close'],
                                    name='Candlestick'), row=1, col=1)
        
        # EMA Lines
        fig.add_trace(go.Scatter(x=self.df.index, y=self.df['ema_30'],
                                mode='lines', name='EMA 30', line=dict(color='blue')), row=1, col=1)
        fig.add_trace(go.Scatter(x=self.df.index, y=self.df['ema_50'],
                                mode='lines', name='EMA 50', line=dict(color='orange')), row=1, col=1)

        # Buy and Sell signals
        buy_signals = self.df[self.df['signal'] == 1]
        sell_signals = self.df[self.df['signal'] == -1]
        fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Low'] * 0.99,
                                mode='markers', name='Buy Signals',
                                marker=dict(symbol='triangle-up', color='green', size=10)), row=1, col=1)
        fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['High'] * 0.99,
                                mode='markers', name='Sell Signals',
                                marker=dict(symbol='triangle-down', color='red', size=10)), row=1, col=1)

        # MACD Indicator
        fig.add_trace(go.Scatter(x=self.df.index, y=self.df['macd'],
                                mode='lines', name='MACD', line=dict(color='purple')), row=2, col=1)
        fig.add_trace(go.Scatter(x=self.df.index, y=self.df['signal_line'],
                                mode='lines', name='Signal Line', line=dict(color='black')), row=2, col=1)
        
        fig.update_layout(title='MACD Trading Strategy',
                        yaxis_title='Price',
                        xaxis_title='Index')
        
        fig.show()



