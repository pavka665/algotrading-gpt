import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from binance import Binance
from bybit import Bybit
from bb_strategy import BBStrategy
from macd_strategy import MACDStrategy
from backtest_gpt4 import Backtest


class Statistics:
    def __init__(self, budget, trade_percentage, leverage):
        self.coin_list = [
            'BTCUSDT', 'ETHUSDT', 'ADAUSDT', 
            'ATOMUSDT', 'LINKUSDT', 'BNBUSDT', 
            'IOTAUSDT', 'ICPUSDT', 'KAVAUSDT',
            'AVAXUSDT', 'AAVEUSDT', 'APEUSDT',
            'ROSEUSDT', 'KLAYUSDT', 'FLOWUSDT',
            'XRPUSDT', 'RUNEUSDT', 'NOTUSDT',
            'SOLUSDT', 'TRXUSDT', 'DOGEUSDT',
            'NEARUSDT', 'DOTUSDT', 'MATICUSDT',
            'UNIUSDT', 'TIAUSDT', 'PYTHUSDT',
            'STRKUSDT', 'FETUSDT','1000PEPEUSDT',
            'AGIXUSDT', 'LDOUSDT', 'TONUSDT'
            'INJUSDT', 'ORDIUSDT', 'GALAUSDT',
            'LTCUSDT'
        ]

        self.coins = [
            'ADAUSDT', 'LINKUSDT', 'KAVAUSDT',
            'APEUSDT', 'ROSEUSDT', 'MATICUSDT',
        ]

        self.months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        self.months_name = ['Янв', 'Февр', 'Март', 'Апр', 'Май', 'Июнь', 'Июль', 'Авг', 'Сент', 'Октб', 'Нояб', 'Дек']
        self.binance = Binance()
        self.bybit = Bybit()
        # self.bb_strategy = BBStrategy()

        self.params = [
            {'take': 2.3, 'stop': 1.8},
            {'take': 2.4, 'stop': 1.9},
            {'take': 2.5, 'stop': 2.0},
            {'take': 2.6, 'stop': 2.1},
            {'take': 2.7, 'stop': 2.2},
            {'take': 2.8, 'stop': 2.3},
            {'take': 2.9, 'stop': 2.4},
            {'take': 3.0, 'stop': 2.5}
        ]

        self.timeframes = ['15m', '30m', '1h', '2h', '4h']

        self.color_initial_budget = '#3742fa'
        self.color_end_budget = '#0652DD'
        self.higher_level = 150
        self.higher_level_color = '#44bd32'
        self.lower_level = 50
        self.lower_level_color = '#ff4757'
        self.figuresize = (20, 12)
        self.layout = 'constrained'

        self.budget = budget
        self.trade_percentage = trade_percentage
        self.leverage = leverage
        
    
    def get_budget_per_month(self, coin, month, timeframe):
        results = []
        df = self.binance.fetch_data_month(coin, month, timeframe)
        # bb_strategy = BBStrategy(df)
        # df = bb_strategy.run(df)
        macd_strategy = MACDStrategy(df)
        df = macd_strategy.run()
        for param in self.params:
            backtest = Backtest(df, self.budget, self.trade_percentage, self.leverage, param['take'], param['stop'])
            stats = backtest.run()
            results.append({
                'params': f"take_{param['take']}_stop_{param['stop']}",
                'end_budget': stats['end_budget'],
                'total_signals': stats['total_signals'],
                'amount_trades': stats['amount_trades']
            })

        fig, ax = plt.subplots(figsize=self.figuresize)
        ax.axhline(y=self.budget, color=self.color_initial_budget, linestyle='--', label='Initial_Budget')
        for result in results:
            ax.bar(result['params'], result['end_budget'], color=self.color_end_budget, label=f"{result['params']} | {result['total_signals']} | {result['amount_trades']} |")
        
        ax.set_ylabel('End Budget')
        ax.set_title(f'Backtest Results {coin} {timeframe} {month}')
        ax.legend()
        plt.show()
        
    def get_budget_per_month_by_coins(self, month, timeframe):
        results = {f"budget_take_{param['take']}_stop_{param['stop']}": [] for param in self.params}
        for coin in self.coins:
            df = self.binance.fetch_data_month(coin, month, timeframe)
            bb_strategy = BBStrategy(df)
            df = bb_strategy.run(df)
            for param in self.params:
                backtest = Backtest(df, self.budget, self.trade_percentage, self.leverage, param['take'], param['stop'])
                stats = backtest.run()
                results[f"budget_take_{param['take']}_stop_{param['stop']}"].append(stats['end_budget'])
        
        x = np.arange(len(self.coins))
        width = 0.15
        multiplier = 0
        fig, ax = plt.subplots(figsize=self.figuresize, layout=self.layout)
        ax.axhline(y=self.budget, color=self.color_initial_budget, linestyle='--', label='Initial Budget')
        for key, value in results.items():
            offset = width * multiplier
            rects = ax.bar(x+offset, value, width, label=key)
            ax.bar_label(rects, padding=3)
            multiplier += 1

        ax.set_ylabel('Budget')
        ax.set_title(f'Backtest Results for coins {month}')
        ax.set_xticks(x+width, self.coins)
        ax.legend(loc='upper left', ncols=len(self.coins) + 1)
        plt.show()


    def get_budget_by_timestamp(self):
        ...   
    
    def get_budget_per_year_for_coins(self, year, timeframe, params):
        results = {coin: [] for coin in self.coins}
        for coin in self.coins:
            for month in self.months:
                df = self.binance.fetch_data_month(coin, f'{year}-{month}', timeframe)
                bb_strategy = BBStrategy(df)
                df = bb_strategy.run(df)
                backtest = Backtest(df, self.budget, self.trade_percentage, self.leverage, params['take'], params['stop'])
                stats = backtest.run()
                results[coin].append(stats['end_budget'])

        x = np.arange(len(self.months))
        width = 0.15
        multiplier = 0
        fig, ax = plt.subplots(figsize=self.figuresize, layout=self.layout)
        ax.axhline(y=self.budget, color=self.color_initial_budget, linestyle='--', label='Initial Budget')
        ax.axhline(y=self.higher_level, color=self.higher_level_color, linestyle='--', linewidth=1.5)
        ax.axhline(y=200, color=self.higher_level_color, linestyle='--', linewidth=1.5)
        ax.axhline(y=self.lower_level, color=self.lower_level_color, linestyle='--', linewidth=1.5)
        for key, value in results.items():
            offset = width * multiplier
            rects = ax.bar(x + offset, value, width, label=key)
            ax.bar_label(rects, padding=3)
            multiplier += 1
        
        ax.set_ylabel('Budget')
        ax.set_title(f"Backtest Results: Timeframe: {timeframe} Take Profit: {params['take']} Stop Loss: {params['stop']}")
        ax.set_xticks(x + width, self.months_name)
        ax.legend(loc='upper left', ncols=7)
        plt.show()

    def get_budget_per_year_for_timeframes(self, coin, year, params):
        results = {timeframe: [] for timeframe in self.timeframes}
        for timeframe in self.timeframes:
            for month in self.months:
                df = self.binance.fetch_data_month(coin, f'{year}-{month}', timeframe)
                bb_strategy = BBStrategy(df)
                df = bb_strategy.run(df)
                backtest = Backtest(df, self.budget, self.trade_percentage, self.leverage, params['take'], params['stop'])
                stats = backtest.run()
                results[timeframe].append(stats['end_budget'])
        
        x = np.arange(len(self.months))
        width = 0.15
        multiplier = 0
        fig, ax = plt.subplots(figsize=self.figuresize, layout=self.layout)
        ax.axhline(y=self.budget, color=self.color_initial_budget, linestyle='--', label='Initial Budget')
        ax.axhline(y=self.higher_level, color=self.higher_level_color, linestyle='--', linewidth=1.5)
        ax.axhline(y=200, color=self.higher_level_color, linestyle='--', linewidth=1.5)
        ax.axhline(y=self.lower_level, color=self.lower_level_color, linestyle='--', linewidth=1.5)
        for key, value in results.items():
            offset = width * multiplier
            rects = ax.bar(x + offset, value, width, label=key)
            ax.bar_label(rects, padding=3)
            multiplier += 1

        ax.set_ylabel('Budget')
        ax.set_title(f"Backtest Results: Coin: {coin} Take Profit: {params['take']} Stop Loss: {params['stop']}")
        ax.set_xticks(x + width, self.months_name)
        ax.legend(loc='upper left', ncols=7)
        plt.show()
            
