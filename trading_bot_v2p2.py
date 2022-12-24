# For the seconde version of our trading bot, we will use the bid/ask price of the order book
# For now, we won't take the bid/ask qty into account and make the hypothesis that we can buy as much of it as we want
# We also want to measure how long an opportunity stay on average

import pandas as pd
import numpy as np

# Loading the data
df_btc_usdt = pd.read_csv('btcusdt_socket_book.csv').astype('float32')
df_eth_usdt = pd.read_csv('ethusdt_socket_book.csv').astype('float32')
df_eth_btc = pd.read_csv('ethbtc_socket_book.csv').astype('float32')

# We add the market for each df
df_btc_usdt['market'] = 'BTCUSDT'
df_eth_usdt['market'] = 'ETHUSDT'
df_eth_btc['market'] = 'ETHBTC'

# We look for the lowest last timestamps amoung the 3 df
lower_max_timestamps = min(df_btc_usdt['timestamps'].iloc[-1],df_eth_usdt['timestamps'].iloc[-1],df_eth_btc['timestamps'].iloc[-1])
higher_min_timestamps = max(df_btc_usdt['timestamps'].iloc[0],df_eth_usdt['timestamps'].iloc[0],df_eth_btc['timestamps'].iloc[0])

print(higher_min_timestamps,lower_max_timestamps)

#We merge the 3 df and sort them by ascending timestamps
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

# Variable to track when we are doing an arbitrage
arb_possible = []


for i in range(df.shape[0]):

    if df['timestamps'][i]>lower_max_timestamps:
        break

    # update asks and bids
    if df['market'][i] == 'BTCUSDT':
        btc_usdt_bid = df['bid_price'][i]
        btc_usdt_ask = df['ask_price'][i]
        btc_usdt_bid_qty = df['bid_qty'][i]
        btc_usdt_ask_qty = df['ask_qty'][i]
    elif df['market'][i] == 'ETHUSDT':
        eth_usdt_bid = df['bid_price'][i]
        eth_usdt_ask = df['ask_price'][i]
        eth_usdt_bid_qty = df['bid_qty'][i]
        eth_usdt_ask_qty = df['ask_qty'][i]
    else:
        eth_btc_bid = df['bid_price'][i]
        eth_btc_ask = df['ask_price'][i]
        eth_btc_bid_qty = df['bid_qty'][i]
        eth_btc_ask_qty = df['ask_qty'][i]

    # if all market is found once
    if all([btc_usdt_bid,eth_usdt_bid,eth_btc_bid]):


        # if we can make a profit with buy btc_usdt, buy eth_btc and sell eth_usdt
        if btc_usdt_bid*fee3>eth_usdt_ask/eth_btc_bid:

            # looking for the biggest possible position with the current order book
            position_max = min(eth_btc_bid_qty*eth_btc_bid*btc_usdt_bid,btc_usdt_bid_qty*btc_usdt_bid,eth_usdt_ask_qty*eth_usdt_ask,eth_btc_bid_qty*eth_usdt_ask,cash)

            # position_max is the biggest cash position we can take from this move,
            # step 1 : We withdraw it from our cash reserve
            cash-=position_max
            # step 2 : We multiply by the gain we can make on this position
            position_max *= btc_usdt_bid*eth_btc_bid/eth_usdt_ask*fee3
            # step 3 : we add it back to the cash
            cash+=position_max

            #keep track of when an arbitrage is possible
            arb_possible.append(i)

        # if we can make a profit with sell btc_usdt, sell eth_btc and buy eth_usdt
        elif btc_usdt_ask<eth_usdt_bid/eth_btc_ask*fee3:
            # looking for the biggest possible position with the current order book
            postion_max = min(eth_btc_ask_qty*eth_btc_ask*btc_usdt_ask,btc_usdt_ask_qty*btc_usdt_ask,eth_usdt_bid_qty*eth_usdt_bid,eth_btc_ask_qty*eth_usdt_bid,cash)
            cash-=postion_max
            postion_max *= eth_usdt_bid/(btc_usdt_ask*eth_btc_ask)*fee3
            cash+=postion_max
            arb_possible.append(i)
        cash_time.append(cash)



#print(arb_possible)
print(cash)
print(len(arb_possible))
print(len(cash_time))
print((cash/1000000-1)*100)
cash_time = np.array(cash_time)/1000000

import matplotlib.pyplot as plt
plt.plot(cash_time)
plt.title("Evolution of the cash position")
plt.xlabel("Time")
plt.ylabel("Cash ($M)")

plt.show()
