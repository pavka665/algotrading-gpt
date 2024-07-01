import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from bybit import Bybit
from binance import Binance
from backtest_gpt4 import Backtest
from backtest import Backtest as BTest

class MACDStrategy:
    def __init__(self, df, short_window=12, long_window=26, signal_window=9):
        self.df = df
        self.short_window = short_window
        self.long_window = long_window
        self.signal_window = signal_window
        self._calculate_macd()

    def _calculate_macd(self):
        self.df['ema_short'] = self.df['Close'].ewm(span=self.short_window, adjust=False).mean()
        self.df['ema_long'] = self.df['Close'].ewm(span=self.long_window, adjust=False).mean()
        self.df['macd'] = self.df['ema_short'] - self.df['ema_long']
        self.df['signal_line'] = self.df['macd'].ewm(span=self.signal_window, adjust=False).mean()
        self.df['hist'] = self.df['macd'] - self.df['signal_line']


    def run(self):
        buy_signal = (self.df['macd'].shift(1) < self.df['signal_line'].shift(1)) & (self.df['macd'] > self.df['signal_line'])
        sell_signal = (self.df['macd'].shift(1) > self.df['signal_line'].shift(1)) & (self.df['macd'] < self.df['signal_line'])
        self.df['Buy'] = np.where(buy_signal, self.df['Close'], np.nan)
        self.df['Sell'] = np.where(sell_signal, self.df['Close'], np.nan)
        self.df['signal'] = 0
        self.df['signal'] = np.where(buy_signal, 1, self.df['signal'])
        self.df['signal'] = np.where(sell_signal, -1, self.df['signal'])
        self.df['pointpos'] = self.df.apply(lambda row: self.pointpos(row), axis=1)
        return self.df

    def pointpos(self, row):
        if row['signal'] == 1:
            return row['Low'] - 1e-4
        elif row['signal'] == -1:
            return row['High'] + 1e-4
        else:
            return np.nan



if __name__ == '__main__':
    # bybit = Bybit()
    # df = bybit.get_klines('RUNEUSDT', 30, limit=500)
    # macd_strategy = MACDStrategy(df)
    # macd_strategy.run()
    # backtest = Backtest(df, 100, 0.2, 20, 2.2, 1.8)
    # stats = backtest.run()
    # print(f"Period: {stats['period']}\t|Start Budget: {stats['start_budget']}\t|End Budget: {stats['end_budget']}\t|Total Signals {stats['total_signals']}\t| Amount Trades: {stats['amount_trades']}")
    # for trade in stats['trades']:
    #     print(f"{trade['trade_type']}\t{trade['entry_budget']}\t{trade['exit_budget']}\t{trade['profit']}")
    # backtest.plot()
    # b_test = BTest(df, 100, 0.1, 20, 14, 2.5, 2)
    # stats = b_test.run()
    # print(f"Period: {stats['period']}\t|Start Budget: {stats['start_budget']}\t|End Budget: {stats['end_budget']}\t|Total Signals {stats['total_signals']}\t| Amount Trades: {stats['amount_trades']}")
    # for trade in stats['trades']:
    #     print(f"{trade['trade_type']}\t{trade['entry_budget']}\t{trade['exit_budget']}\t{trade['profit']}")
    # b_test.plot()
    # binance = Binance()
    # coins = ['BTCUSDT', 'ADAUSDT', 
    #         'ATOMUSDT', 'LINKUSDT',
    #         'KAVAUSDT', 'AVAXUSDT',
    #         'XRPUSDT', 'RUNEUSDT',
    #         'DOGEUSDT', 'NEARUSDT']

    # results = []
    # for coin in coins:
    #     df = binance.fetch_data_month(coin, '2024-03', '30m')
    #     macd_strategy = MACDStrategy(df)
    #     df = macd_strategy.run()
    #     backtest = Backtest(df, 100, 0.2, 20, 2.3, 1.8)
    #     stats = backtest.run()
    #     results.append({
    #         'coin': coin,
    #         'start_budget': stats['start_budget'],
    #         'end_budget': stats['end_budget'],
    #         'period': stats['period']
    #     })
    
    # fig, ax = plt.subplots(figsize=(12,8))

    # ax.axhline(y=100, color='blue', linestyle='--', label='Initial Budget')
    # for result in results:
    #     ax.bar(result['coin'], result['end_budget'], label=f"{result['coin']} ({result['period']})")

    # ax.set_xlabel("Coin")
    # ax.set_ylabel("End Budget")
    # ax.set_title("Backtest Results for Multiple Coins")
    # ax.legend()

    # plt.show()
    binance = Binance()
    coin = 'ADAUSDT'
    results = []
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    for month in months:
        df = binance.fetch_data_month(coin, f'2023-{month}', '4h')
        macd_strategy = MACDStrategy(df)
        df = macd_strategy.run()
        backtest = Backtest(df, 100, 0.2, 20, 2.3, 1.8)
        stats = backtest.run()
        results.append({
            'coin': coin,
            'month': month,
            'start_budget': stats['start_budget'],
            'end_budget': stats['end_budget'],
            'total_signals': stats['total_signals'],
            'amount_trades': stats['amount_trades']
        })

    fig, ax = plt.subplots(figsize=(12,8))
    ax.axhline(y=100, color='#e056fd', linestyle='--', label='Initial Budget')
    for result in results:
        ax.bar(result['month'], result['end_budget'], color='#686de0', label=f"{result['month']} ({result['total_signals']} | {result['amount_trades']})")

    ax.set_xlabel('Month')
    ax.set_ylabel('End Budget')
    ax.set_title('Backtest Results for Year')
    ax.legend()
    plt.show()

