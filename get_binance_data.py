#Get OHLCV for BTC/UDT ETH/USDT and BTC/USDT
#Download Prices from Binance and Coinbase and put them on a .csv file
# This time, we keep the date,O,H,L,C,V data

import requests
import time
import pandas as pd
import numpy as np

now = int(time.time()*1000)
now = now - now%(60*1000)#rounding to the lowest min


def get_ohlcv(ticker,now):
    binance_main_url = 'https://api.binance.com'
    binance_start_time = now-60*1000*1000
    binance_end_time = now
    b_close = []
    b_open = []
    b_high = []
    b_low = []
    b_volume = []
    binance_timestamps = []

    data_len = 2880
    for i in range(data_len):
        binance_url = binance_main_url+ '/api/v3/klines?symbol='+ticker+'&interval=1m&startTime='+str(binance_start_time)+'&endTime='+str(binance_end_time)+'&limit=1000'
        binance_end_time = binance_start_time -1
        binance_start_time = binance_end_time - 60*1000*1000
        response = requests.get(binance_url)
        response = response.json()

        if len(response) < 100:
            print(response,i)
            break

        for j in range(len(response)):
            binance_timestamps.append(response[j][0]/1000)
            b_open.append(response[j][1])
            b_high.append(response[j][2])
            b_low.append(response[j][3])
            b_close.append(response[j][4])
            b_volume.append(response[j][5])
        if i%(data_len//10)==0:
            print(f'Binance {ticker} advancement : {i*100/data_len:0.2f} %')

    # round binance timestamps
    binance_timestamps = list(map(int, binance_timestamps))


    print(f'Binance {ticker} time : {time.time()-now/1000}')


    df = pd.DataFrame({'Open':b_open,'High':b_high,'Low':b_low,'Close':b_close,'Volume':b_volume}, index = binance_timestamps)
    df = df.sort_index(ascending=False)
    df.fillna('',inplace=True)
    df = df[df['Close']!='']
    return df

df_btc_usdt = get_ohlcv('BTCUSDT',now)
df_eth_usdt = get_ohlcv('ETHUSDT',now)
df_btc_eth = get_ohlcv('ETHBTC',now)

min_len = min(df_btc_usdt.shape[0],df_eth_usdt.shape[0],df_btc_eth.shape[0])
df_btc_usdt = df_btc_usdt.iloc[:min_len]
df_eth_usdt = df_eth_usdt.iloc[:min_len]
df_btc_eth = df_btc_eth.iloc[:min_len]

df_btc_usdt = df_btc_usdt.sort_index(ascending=True)
df_eth_usdt = df_eth_usdt.sort_index(ascending=True)
df_btc_eth = df_btc_eth.sort_index(ascending=True)

df_btc_usdt.to_csv('BTCUSDT_ohlcv_binance_minutes.csv')
df_eth_usdt.to_csv('ETHUSDT_ohlcv_binance_minutes.csv')
df_btc_eth.to_csv('ETHBTC_ohlcv_binance_minutes.csv')
