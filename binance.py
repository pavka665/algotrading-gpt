import pandas as pd
import requests
import datetime

class Binance:
    def __init__(self):
        self.base_url = 'https://fapi.binance.com'

    def get_klines(self, symbol, interval, limit=500):
        url = f'{self.base_url}/fapi/v1/klines'
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        df = pd.DataFrame(requests.get(url=url, params=params).json())
        df = df.iloc[:,0:6]
        df.columns = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        df['Open Time'] = [datetime.datetime.fromtimestamp(x / 1000) for x in df['Open Time']]
        df['Open'] = df['Open'].astype(float)
        df['High'] = df['High'].astype(float)
        df['Low'] = df['Low'].astype(float)
        df['Close'] = df['Close'].astype(float)
        df['Volume'] = df['Volume'].astype(float)
        return df

    def fetch_data_month(self, symbol, month, interval):
        url = f'{self.base_url}/fapi/v1/klines'
        start_date = datetime.datetime.strptime(f'{month}-01', '%Y-%m-%d')
        end_date = (start_date + datetime.timedelta(days=31)).replace(day=1) - datetime.timedelta(seconds=1)
        limit = 1500
        all_data = []

        while start_date < end_date:
            start_timestamp = int(start_date.timestamp() * 1000)
            end_timestamp = int((start_date + datetime.timedelta(minutes=30*limit)).timestamp() * 1000)
            params = {
                'symbol': symbol,
                'interval': interval,
                'startTime': start_timestamp,
                'endTime': end_timestamp,
                'limit': limit
            }
            response = requests.get(url, params=params)
            data = response.json()
            all_data.extend(data)
            if len(data) < limit:
                break
            last_entry = data[-1][0]
            start_date = datetime.datetime.fromtimestamp(last_entry / 1000)
        
        df = pd.DataFrame(all_data)
        df = df.iloc[:,0:6]
        df.columns = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        df['Open Time'] = [datetime.datetime.fromtimestamp(x / 1000) for x in df['Open Time']]
        df['Open'] = df['Open'].astype(float)
        df['High'] = df['High'].astype(float)
        df['Low'] = df['Low'].astype(float)
        df['Close'] = df['Close'].astype(float)
        df['Volume'] = df['Volume'].astype(float)
        return df
    
        


if __name__ == '__main__':
    binance = Binance()

    data = binance.fetch_data_month('BTCUSDT', '2024-04', '1h')
    print(data)