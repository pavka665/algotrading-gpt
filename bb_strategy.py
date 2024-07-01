import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from bybit import Bybit
from binance import Binance
from tqdm import tqdm
from backtest_gpt4 import Backtest
from backtest import Backtest as BTest 

tqdm.pandas()


class BBStrategy:
    def __init__(self, df, ema_fast=30, ema_slow=50, bb_ma='SMA', bb_window=15, bb_std=1.5):
        self.df = df
        self.backcandles = 7
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        self.bb_ma = bb_ma          # Bollinger Bands Moving Average which can be SMA or EMA
        self.bb_window = bb_window  # Window for calculating the Bollinger Bands
        self.bb_std = bb_std        # Standart Divietion for calculating the Bollinger Bands

        self._calculate_ema()
        self._calculate_bb()

    def _calculate_ema(self):
        self.df['ema_fast'] = self.df['Close'].ewm(span=self.ema_fast, adjust=False).mean()
        self.df['ema_slow'] = self.df['Close'].ewm(span=self.ema_slow, adjust=False).mean()

    def _calculate_bb(self):
        if self.bb_ma == 'SMA':
            self.df['bb_sma'] = self.df['Close'].rolling(window=self.bb_window).mean()
            self.df['bb_std'] = self.df['Close'].rolling(window=self.bb_window).std()
            self.df['b_upper'] = self.df['bb_sma'] + (self.df['bb_std'] * self.bb_std)
            self.df['b_lower'] = self.df['bb_sma'] - (self.df['bb_std'] * self.bb_std)
        elif self.bb_ma == 'EMA':
            self.df['bb_ema'] = self.df['Close'].ewm(span=self.bb_window, adjust=False).mean()
            self.df['bb_std'] = self.df['Close'].ewm(span=self.bb_window, adjust=False).std()
            self.df['b_upper'] = self.df['bb_ema'] + (self.df['bb_std'] * self.bb_std)
            self.df['b_lower'] = self.df['bb_ema'] - (self.df['bb_std'] * self.bb_std)

    def check_trend(self, index):
        # This method check if the market is in up trend or down trand
        # For up trand return 1 and for down trand return -1
        df_slice = self.df.reset_index().copy()
        start = max(0, index - self.backcandles)
        end = index
        relevant_rows = df_slice.iloc[start:end]
        
        if all(relevant_rows['ema_fast'] > relevant_rows['ema_slow']):
            return 1
        elif all(relevant_rows['ema_fast'] < relevant_rows['ema_slow']):
            return -1
        else:
            return 0

    def generate_signals(self, index):
        if (self.check_trend(index) == 1 and self.df['Close'][index] <= self.df['b_lower'][index]):
            return 1
        if (self.check_trend(index) == -1 and self.df['Close'][index] >= self.df['b_upper'][index]):
            return -1
        return 0


    def run(self, df):
        self.df['signal'] = self.df.progress_apply(lambda row: self.generate_signals(row.name), axis=1)
        self.df['pointpos'] = self.df.apply(lambda row: self.pointpos(row), axis=1)
        return self.df

    def pointpos(self, row):
        if row['signal'] == 1:
            return row['Low'] - 1e-4
        elif row['signal'] == -1:
            return row['High'] + 1e-4
        else:
            return np.nan

    def plot(self):
        fig = go.Figure(data=[go.Candlestick(x=self.df.index,
                            open=self.df['Open'],
                            high=self.df['High'],
                            low=self.df['Low'],
                            close=self.df['Close']),
                            
                            go.Scatter(x=self.df.index, y=self.df['b_lower'],
                                    line=dict(color='green', width=1), name='BB Lower'),
                                    
                            go.Scatter(x=self.df.index, y=self.df['b_upper'],
                                    line=dict(color='red', width=1), name='BB Upper'),
                                    
                            go.Scatter(x=self.df.index, y=self.df['ema_fast'],
                                    line=dict(color='black', width=1.5), name='EMA Fast'),
                                    
                            go.Scatter(x=self.df.index, y=self.df['ema_slow'],
                                    line=dict(color='blue', width=1.5), name='EMA Slow')])
        fig.add_scatter(x=self.df.index, y=self.df['pointpos'], mode='markers',
                        marker=dict(size=10, color='MediumPurple'),
                        name='Signals')
        fig.show()


if __name__ == '__main__':
    binance = Binance()
    # bybit = Bybit()
    # df = bybit.get_klines('RUNEUSDT', 30, limit=500)
    # bb_strategy = BBStrategy(df)
    # df = bb_strategy.run(df)

    # df = binance.fetch_data_month('KAVAUSDT', '2022-02', '30m')
    # bb_strategy = BBStrategy(df)
    # df = bb_strategy.run(df)

    # backtest = Backtest(df, 100, 0.2, 20, 2.3, 1.8)
    # stats = backtest.run()
    # print(f"Period: {stats['period']}\t|Start Budget: {stats['start_budget']}\t|End Budget: {stats['end_budget']}\t|Total Signals {stats['total_signals']}\t| Amount Trades: {stats['amount_trades']}")
    # for trade in stats['trades']:
    #     print(f"{trade['trade_type']}\t{trade['entry_budget']}\t{trade['exit_budget']}\t{trade['profit']}")
    # backtest.plot()


    # b_test = BTest(df, 100, 0.3, 20, 14, 1.5, 3)
    # stats = b_test.run()
    # print(f"Period: {stats['period']}\t|Start Budget: {stats['start_budget']}\t|End Budget: {stats['end_budget']}\t|Total Signals {stats['total_signals']}\t| Amount Trades: {stats['amount_trades']}")
    # for trade in stats['trades']:
    #     print(f"{trade['trade_type']}\t{trade['entry_budget']}\t{trade['exit_budget']}\t{trade['profit']}")
    # b_test.plot()


    # coins = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 
    #         'ATOMUSDT', 'LINKUSDT', 'BNBUSDT', 
    #         'IOTAUSDT', 'ICPUSDT', 'KAVAUSDT',
    #         'AVAXUSDT', 'AAVEUSDT', 'APEUSDT',
    #         'ROSEUSDT', 'KLAYUSDT', 'FLOWUSDT',
    #         'XRPUSDT', 'RUNEUSDT', 'NOTUSDT',
    #         'SOLUSDT', 'TRXUSDT', 'DOGEUSDT',
    #         'NEARUSDT', 'DOTUSDT', 'MATICUSDT',
    #         'UNIUSDT', 'TIAUSDT', 'PYTHUSDT',
    #         'STRKUSDT', 'FETUSDT','1000PEPEUSDT',
    #         'AGIXUSDT', 'LDOUSDT',
    #         'INJUSDT', 'ORDIUSDT', 'GALAUSDT']


    # Run strategy to coin list and get chart with data per month ====================================
    # coins = ['BTCUSDT', 'ADAUSDT', 
    #         'ATOMUSDT', 'LINKUSDT',
    #         'KAVAUSDT', 'AVAXUSDT',
    #         'XRPUSDT', 'RUNEUSDT',
    #         'DOGEUSDT', 'NEARUSDT']

    # results = []
    # for coin in coins:
    #     df = binance.fetch_data_month(coin, '2024-05', '30m')
    #     bb_strategy = BBStrategy(df)
    #     df = bb_strategy.run(df)
    #     backtest = Backtest(df, 100, 0.2, 20, 2.4, 1.9)
    #     stats = backtest.run()
    #     results.append({
    #         'coin': coin,
    #         'start_budget': stats['start_budget'],
    #         'end_budget': stats['end_budget'],
    #         'period': stats['period'],
    #         'total_signals': stats['total_signals'],
    #         'amount_trades': stats['amount_trades']
    #     })
    
    # fig, ax = plt.subplots(figsize=(12,8))

    # ax.axhline(y=100, color='blue', linestyle='--', label='Initial Budget')
    # for result in results:
    #     ax.bar(result['coin'], result['end_budget'], label=f"{result['coin']} ({result['total_signals']} | {result['amount_trades']})")

    # ax.set_xlabel("Coin")
    # ax.set_ylabel("End Budget")
    # ax.set_title("Backtest Results for Multiple Coins")
    # ax.legend()

    # plt.show()
    # END ===============================================================================================
    # backtest = Backtest(100, 0.2, 20, 2.3, 1.8)
    # coin = 'TONUSDT'
    # results = []
    # months = ['05']
    # for month in months:
    #     df = binance.fetch_data_month(coin, f'2024-{month}', '5m')
    #     bb_strategy = BBStrategy(df)
    #     df = bb_strategy.run(df)
    #     backtest = Backtest(df, 100, 0.2, 20, 2.3, 1.8)
    #     stats = backtest.run(df)
    #     results.append({
    #         'coin': coin,
    #         'month': month,
    #         'start_budget': stats['start_budget'],
    #         'end_budget': stats['end_budget'],
    #         'total_signals': stats['total_signals'],
    #         'amount_trades': stats['amount_trades']
    #     })

    # fig, ax = plt.subplots(figsize=(12,8))
    # ax.axhline(y=100, color='#e056fd', linestyle='--', label='Initial Budget')
    # for result in results:
    #     ax.bar(result['month'], result['end_budget'], color='#686de0', label=f"{result['month']} ({result['total_signals']} | {result['amount_trades']})")
    # ax.set_xlabel('Month')
    # ax.set_ylabel('End Budget')
    # ax.set_title('Backtest Results for Year')
    # ax.legend()
    # plt.show()

    # coin = 'ADAUSDT'
    # months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    # months_name = ['Янв', 'Февр', 'Март', 'Апр', 'Май', 'Июнь', 'Июль', 'Авг', 'Сент', 'Октб', 'Нояб', 'Дек']
    # # months = ['01', '02']
    # # months_name = ['Янв', 'Февр']
    # results = {}
    # params = [
        # {'take': 2.3, 'stop': 1.8},
        # {'take': 2.4, 'stop': 1.9},
        # {'take': 2.5, 'stop': 2.0},
        # {'take': 2.6, 'stop': 2.1},
        # {'take': 2.7, 'stop': 2.2},
        # {'take': 2.8, 'stop': 2.3},
        # {'take': 2.9, 'stop': 2.4},
        # {'take': 3.0, 'stop': 2.5},
    # ]
    # for param in params:
    #     results[f"budget_take_{param['take']}_stop_{param['stop']}"] = []
# results = {f"budget_take_{param['take']}_stop_{param['stop']}": [] for param in params}

    # for month in months:
    #     df = binance.fetch_data_month(coin, f'2023-{month}', '30m')
    #     bb_strategy = BBStrategy(df)
    #     df = bb_strategy.run(df)
    #     for param in params:
    #         backtest = Backtest(df, 100, 0.2, 20, param['take'], param['stop'])
    #         stats = backtest.run()
    #         results[f"budget_take_{param['take']}_stop_{param['stop']}"].append(stats['end_budget'])

    
    # x = np.arange(len(months))
    # width = 0.1
    # multiplier = 0
    # fig, ax = plt.subplots(figsize=(18,12), layout='constrained')
    # ax.axhline(y=100, color='#e056fd', linestyle='--', label='Initial Budget')
    # for key, value in results.items():
    #     offset = width * multiplier
    #     rects = ax.bar(x + offset, value, width, label=key)
    #     ax.bar_label(rects, padding=3)
    #     multiplier += 1
    
    # ax.set_ylabel('Budget')
    # ax.set_title(f'Backtest Results {coin}')
    # ax.set_xticks(x+width, months_name)
    # ax.legend(loc='upper left', ncols=6)
    # plt.show()





    


    

    # COIN INFORMATION====================================
    # coin_data = {
    #     'BTCUSDT': 2019-09-01 02:00:00,
    #     'ETHUSDT': 2019-11-01 01:00:00,
    #     'ADAUSDT': 2020-01-01 01:00:00,
    #     'ATOMUSDT': 2020-02-01 01:00:00,
    #     'LINKUSDT': 2020-01-01 01:00:00,
    #     'BNBUSDT': 2020-02-01 01:00:00,
    #     'IOTAUSDT': 2020-02-01 01:00:00,
    #     'ICPUSDT': 2022-09-01 02:00:00,
    #     'KAVAUSDT': 2020-07-01 02:00:00,
    #     'AVAXUSDT': 2020-09-01 02:00:00,
    #     'AAVEUSDT': 2020-10-01 02:00:00,
    #     'APEUSDT': 2022-03-01 01:00:00,
    #     'ROSEUSDT': 2021-12-01 01:00:00,
    #     'KLAYUSDT': 2021-10-01 02:00:00,
    #     'FLOWUSDT': 2022-02-01 01:00:00,
    #     'XRPUSDT': 2020-01-01 01:00:00,
    #     'RUNEUSDT': 2020-09-01 02:00:00,
    #     'NOTUSDT': 2024-05-01 02:00:00,
    #     'SOLUSDT': 2020-09-01 02:00:00,
    #     'TRXUSDT': 2020-01-01 01:00:00,
    #     'DOGEUSDT': 2020-07-01 02:00:00,
    #     'NEARUSDT': 2020-10-01 02:00:00,
    #     'DOTUSDT': 2020-08-01 02:00:00,
    #     'MATICUSDT': 2020-10-01 02:00:00,
    #     'UNIUSDT': 2020-09-01 02:00:00,
    #     'TIAUSDT': 2023-10-01 02:00:00,
    #     'PYTHUSDT': 2023-11-01 01:00:00,
    #     'STRKUSDT': 2024-02-01 01:00:00,
    #     'FETUSDT': 2023-01-01 01:00:00,
    #     '1000PEPEUSDT': 2023-05-01 02:00:00,
    #     'AGIXUSDT': 2023-02-01 01:00:00,
    #     'LDOUSDT': 2022-09-01 02:00:00,
    #     'INJUSDT': 2022-08-01 02:00:00,
    #     'ORDIUSDT': 2023-11-01 01:00:00,
    #     'GALAUSDT': 2021-09-01 02:00:00
    # }


