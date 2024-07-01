import pandas as pd 
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class Backtest:
    def __init__(self, df: pd.DataFrame, initial_budget: float, trade_percentage: float, leverage: int, atr_period: int, tp_multiplier: float, sl_multiplier: float):
        self.df = df
        self.initial_budget = initial_budget
        self.trade_percentage = trade_percentage
        self.leverage = leverage
        self.atr_period = atr_period
        self.tp_multiplier = tp_multiplier
        self.sl_multiplier = sl_multiplier
        self.trades = []
        self.final_budget = initial_budget
        self.df['atr'] = self._calculate_atr(self.df, atr_period)

    def _calculate_atr(self, data, period):
        data['H-L'] = data['High'] - data['Low']
        data['H-PC'] = abs(data['High'] - data['Close'].shift(1))
        data['L-PC'] = abs(data['Low'] - data['Close'].shift(1))
        data['TR'] = data[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        atr = data['TR'].rolling(window=period, min_periods=1).mean()
        return atr

    def run(self):
        budget = self.initial_budget
        in_position = False
        entry_price = 0
        entry_index = 0
        entry_date = None
        trade_type = None

        for index, row in self.df.iterrows():
            if not in_position:
                if row['signal'] == 1 or row['signal'] == -1:
                    in_position = True
                    entry_price = row['Close']
                    entry_index = index
                    entry_date = row['Open Time']
                    trade_type = 'long' if row['signal'] == 1 else 'short'
                    entry_budget = budget
                    atr_value = row['atr']
                    stop_loss = atr_value * self.sl_multiplier
                    take_profit = atr_value * self.tp_multiplier
            else:
                if trade_type == 'long':
                    if row['High'] >= entry_price + take_profit or row['Low'] <= entry_price - stop_loss:
                        exit_price = entry_price + take_profit if row['High'] >= entry_price + take_profit else entry_price - stop_loss
                        profit = (exit_price - entry_price) * self.leverage * self.trade_percentage * budget / entry_price
                        budget += profit
                        exit_budget = budget
                        in_position = False
                        self.trades.append({
                            'entry_date': entry_date,
                            'exit_date': row['Open Time'],
                            'period': (row['Open Time'] - entry_date).total_seconds() / 3600,
                            'trade_type': trade_type,
                            'entry_budget': entry_budget,
                            'exit_budget': exit_budget,
                            'profit': profit,
                            'entry_price': entry_price,
                            'take_profit': entry_price + take_profit,
                            'stop_loss': entry_price - stop_loss
                        })
                elif trade_type == 'short':
                    if row['Low'] <= entry_price - take_profit or row['High'] >= entry_price + stop_loss:
                        exit_price = entry_price - take_profit if row['Low'] <= entry_price - take_profit else entry_price + stop_loss
                        profit = (entry_price - exit_price) * self.leverage * self.trade_percentage * budget / entry_price
                        budget += profit
                        exit_budget = budget
                        in_position = False
                        self.trades.append({
                            'entry_date': entry_date,
                            'exit_date': row['Open Time'],
                            'period': (row['Open Time'] - entry_date).total_seconds() / 3600,
                            'trade_type': trade_type,
                            'entry_budget': entry_budget,
                            'exit_budget': exit_budget,
                            'profit': profit,
                            'entry_price': entry_price,
                            'take_profit': entry_price - take_profit,
                            'stop_loss': entry_price + stop_loss
                        })

        self.final_budget = budget
        return self._generate_statistics()

    def plot(self):
        budgets = [self.initial_budget]
        for trade in self.trades:
            budgets.append(trade['exit_budget'])

        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.02,
                            row_heights=[0.2, 0.6, 0.2],
                            specs=[[{'type': 'scatter'}],
                                    [{'type': 'candlestick'}],
                                    [{'type': 'bar'}]])

        fig.add_trace(go.Scatter(x=[trade['exit_date'] for trade in self.trades], y=budgets[1:], mode='lines', name='Budget'), row=1, col=1)

        fig.add_trace(go.Candlestick(x=self.df['Open Time'],
                                    open=self.df['Open'],
                                    low=self.df['Low'],
                                    high=self.df['High'],
                                    close=self.df['Close'],
                                    name='Price'), row=2, col=1)
        fig.add_trace(go.Scatter(x=self.df['Open Time'], y=self.df['pointpos'], mode='markers',
                        marker=dict(size=10, color='MediumPurple'), name='Signals'), row=2, col=1)

        for trade in self.trades:
            fig.add_shape(type='rect',
                        x0=trade['entry_date'], y0=trade['entry_price'] * 0.95, x1=trade['exit_date'], y1=trade['entry_price'] * 1.05,
                        xref='x2', yref='y2',
                        fillcolor='LightBlue' if trade['trade_type'] == 'long' else 'LightSalmon',
                        opacity=0.5, layer='below', line_width=0)
            fig.add_trace(go.Scatter(x=[trade['entry_date'], trade['exit_date']],
                                    y=[trade['take_profit'], trade['take_profit']],
                                    mode='lines', name='Take Profit', line=dict(color='green', dash='dash')), row=2, col=1)
            fig.add_trace(go.Scatter(x=[trade['entry_date'], trade['exit_date']],
                                    y=[trade['stop_loss'], trade['stop_loss']],
                                    mode='lines', name='Stop Loss', line=dict(color='red', dash='dash')), row=2, col=1)

        fig.add_trace(go.Bar(x=self.df['Open Time'], y=self.df['Volume'], name='Volume'), row=3, col=1)

        fig.update_layout(title='Backtest Results', xaxis_title='Time', showlegend=False)
        fig.show()

    def _generate_statistics(self):
        total_signals = len(self.df[self.df['signal'] != 0])
        amount_trades = len(self.trades)
        peak_budget = max([trade['exit_budget'] for trade in self.trades] + [self.initial_budget])
        final_result_percentage = ((self.final_budget - self.initial_budget) / self.initial_budget) * 100

        return {
            'period': self.df['Open Time'].iloc[-1] - self.df['Open Time'].iloc[0],
            'start_budget': self.initial_budget,
            'end_budget': self.final_budget,
            'peak_budget': peak_budget,
            'final_result_percentage': final_result_percentage,
            'amount_trades': amount_trades,
            'total_signals': total_signals,
            'trades': self.trades
        }
                        


