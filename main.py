from statistics import Statistics

coin = 'RUNEUSDT'
month = '2024-05'
timeframe = '1h'

budget = 100
trade_percentage = 0.2
leverage = 20

statistics = Statistics(budget, trade_percentage, leverage)
# statistics.get_budget_per_month(coin, month, timeframe)
statistics.get_budget_per_month_by_coins(month, timeframe)

