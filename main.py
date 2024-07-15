from statistics import Statistics
from backtest_gpt4 import Backtest
from binance import Binance
from bb_strategy import BBStrategy

coin = 'ETHUSDT'
month = '2024-06'
timeframe = '15m'

budget = 1000
trade_percentage = 0.2
leverage = 20

params = [
    {'take': 2.3, 'stop': 1.8},
    {'take': 2.4, 'stop': 1.9},
    {'take': 2.5, 'stop': 2.0},
    {'take': 2.6, 'stop': 2.1},
    {'take': 2.7, 'stop': 2.2},
    {'take': 2.8, 'stop': 2.3},
    {'take': 2.9, 'stop': 2.4},
    {'take': 3.0, 'stop': 2.5}
]
# binance = Binance()
# df = binance.fetch_data_month(coin, month, timeframe)
# bb_strategy = BBStrategy(df)
# df = bb_strategy.run(df)
# param = params[0]
# backtest = Backtest(df, budget, trade_percentage, leverage, param['take'], param['stop'])
# stat = backtest.run()
# backtest.plot()

statistics = Statistics(budget, trade_percentage, leverage)
# statistics.get_budget_per_month(coin, month, timeframe)
statistics.get_budget_per_year_for_coins(2023, '30m', params[0])
# statistics.get_budget_per_year_for_timeframes(coin, 2023, params[2])

