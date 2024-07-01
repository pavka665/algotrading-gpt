import pandas as pd 
import requests
import json
from datetime import datetime as dt 


class Bybit:
    def __init__(self):
        self.base_url = 'https://api.bybit.com'

    def get_klines(self, symbol, interval, category='linear', start=None, end=None, limit=200):
        url = f'{self.base_url}/v5/market/kline'
        params = {
            'symbol': symbol,
            'interval': interval,
            'category': category,
            'start': start,
            'end': end,
            'limit': limit
        }
        result = json.loads(requests.get(url, params=params).text)['result']
        df = pd.DataFrame(result['list'])
        df = df.iloc[:,0:6]
        df = df.iloc[::-1].reset_index(drop=True)
        df.columns = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        df['Open Time'] = [dt.fromtimestamp(int(x) / 1000) for x in df['Open Time']]
        df['Open'] = df['Open'].astype(float)
        df['High'] = df['High'].astype(float)
        df['Low'] = df['Low'].astype(float)
        df['Close'] = df['Close'].astype(float)
        df['Volume'] = df['Volume'].astype(float)
        return df
