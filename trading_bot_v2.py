# For the seconde version of our trading bot, we will use the bid/ask price of the order book
# For now, we won't take the bid/ask qty into account and make the hypothesis that we can buy as much of it as we want
# We also want to measure how long an opportunity stay on average

import pandas as pd
import numpy as np


df_btc_usdt = pd.read_csv('btcusdt_socket_book.csv').astype('float32')
df_eth_usdt = pd.read_csv('ethusdt_socket_book.csv').astype('float32')
df_eth_btc = pd.read_csv('ethbtc_socket_book.csv').astype('float32')

df_btc_usdt['market'] = 'BTCUSDT'
df_eth_usdt['market'] = 'ETHUSDT'
df_eth_btc['market'] = 'ETHBTC'


lower_max_timestamps = min(df_btc_usdt['timestamps'].iloc[-1],df_eth_usdt['timestamps'].iloc[-1],df_eth_btc['timestamps'].iloc[-1])
higher_min_timestamps = max(df_btc_usdt['timestamps'].iloc[0],df_eth_usdt['timestamps'].iloc[0],df_eth_btc['timestamps'].iloc[0])

df = pd.concat([df_btc_usdt,df_eth_usdt,df_eth_btc],ignore_index=True)
df.sort_values(by=['timestamps'],ascending=True,ignore_index=True,inplace=True)

btc_usdt_bid = None
eth_usdt_bid = None
eth_btc_bid = None

# trading fee
fee = 0.0000 #0.01 = 1%

# fees multiplier for 3 transactions
fee3 = (1-fee)**3
cash = 1000000
cash_time = []
arb_possible = []
#buy_btc = []
for i in range(df.shape[0]):

    if df['timestamps'][i]>lower_max_timestamps:
        break

    # update asks and bids
    if df['market'][i] == 'BTCUSDT':
        btc_usdt_bid = df['bid_price'][i]
        btc_usdt_ask = df['ask_price'][i]
    elif df['market'][i] == 'ETHUSDT':
        eth_usdt_bid = df['bid_price'][i]
        eth_usdt_ask = df['ask_price'][i]
    else:
        eth_btc_bid = df['bid_price'][i]
        eth_btc_ask = df['ask_price'][i]

    # if all market is found once
    if all([btc_usdt_bid,eth_usdt_bid,eth_btc_bid]):


        # if we can make a profit with buy btc_usdt, buy eth_btc and sell eth_usdt
        if btc_usdt_bid*fee3>eth_usdt_ask/eth_btc_bid:
            cash *= btc_usdt_bid*eth_btc_bid/eth_usdt_ask*fee3
            arb_possible.append(i)

        elif btc_usdt_ask<eth_usdt_bid/eth_btc_ask*fee3:
            cash *= eth_usdt_bid/(btc_usdt_ask*eth_btc_ask)*fee3
            arb_possible.append(i)
        cash_time.append(cash)



print(arb_possible)
print(cash)
print(len(arb_possible))
print(len(cash_time))

cash_time = np.array(cash_time)/1000000
#time_day = np.array(range(len(cash_time)))/60/24

import matplotlib.pyplot as plt
plt.plot(cash_time)
plt.title("Evolution of the cash position")
plt.xlabel("Time")
plt.ylabel("Cash ($M)")

plt.show()
