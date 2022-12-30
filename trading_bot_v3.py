# For the seconde version of our trading bot, we will use the bid/ask price of the order book
# For now, we won't take the bid/ask qty into account and make the hypothesis that we can buy as much of it as we want
# We also want to measure how long an opportunity stay on average

import pandas as pd
import numpy as np


def get_full_book(df,i):
    row = df[i]
    bid_price = []
    bid_qty = []
    ask_price = []
    ask_qty = []

    for i in range(1,20):
        bid_price.append(row['bid_price'+str(i)].values[0])
        bid_qty.append(row['bid_qty'+str(i)].values[0])
        ask_price.append(row['ask_price'+str(i)].values[0])
        ask_qty.append(row['ask_qty'+str(i)].values[0])
    return bid_price,bid_qty,ask_price,ask_qty


def find_position_max1(btc_usdt_bid_price,btc_usdt_bid_qty,eth_btc_bid_price,eth_btc_bid_qty,eth_usdt_ask_price,eth_usdt_ask_qty,cash,fee3,eth_btc_full_book_bid_price,eth_btc_full_book_bid_qty,eth_usdt_full_book_ask_price,eth_usdt_full_book_ask_qty,btc_usdt_full_book_bid_price,btc_usdt_full_book_bid_qty):
    #return the biggest cash position we can take on a trade
    # we have 3 trades cash-> btc, btc->eth, eth-> cash


    # step 1 : compare cash vs usdt_qty in btc_usdt

    #maximum amount of usdt on the bid side for btc_usdt
    max_usdt_bid = btc_usdt_bid_price*btc_usdt_bid_qty #usdt
    #maximum amount of usdt we can buy
    max_usdt_pos = min(cash,max_usdt_bid)   #usdt
    #maximum amount of btc that can be bought with this amount of usdt
    btc_qty = btc_usdt_bid_qty * max_usdt_pos / max_usdt_bid    #btc


    # step 2 :  compare btc_qty vs btc qty in eth_btc
    max_btc_bid = eth_btc_bid_price*eth_btc_bid_qty #btc
    max_btc = min(btc_qty,max_btc_bid) #btc
    eth_qty = eth_btc_bid_qty * max_btc / max_btc_bid #eth

    # step 3: compare eth_qty with est qty in eth_usdt
    max_eth_ask = eth_usdt_ask_qty #eth
    max_eth = min(eth_qty,max_eth_bid) #eth
    eth_ask_qty = max_eth   #eth

    #step 4 : convert in usdt (we don't need to compare with cash)
    position_max = eth_ask_qty*eth_usdt_ask_price #usdt

    #variation of the position_max
    cash -= position_max

    position_max *= btc_usdt_bid*eth_btc_bid/eth_usdt_ask*fee3
    cash += position_max

    #to update the new bids/asks qty, we need to backpropagate the max postion
    eth_usdt_ask_qty -= max_eth
    if eth_usdt_ask_qty == 0:
        #update price from full book
        #update qty from full book
        eth_usdt_ask_qty = eth_usdt_full_book_ask_qty.pop(0)
        eth_usdt_ask_price = eth_usdt_full_book_ask_price.pop(0)

    eth_qty = max_eth #eth
    max_btc = eth_qty * max_btc_bid / eth_btc_bid_qty #btc

    eth_btc_bid_qty -= max_btc / eth_btc_bid_price #eth

    if eth_btc_bid_qty == 0:
        #update price and qty
        eth_btc_bid_qty = eth_btc_full_book_bid_qty.pop(0)
        eth_btc_bid_price = eth_btc_full_book_bid_price.pop(0)

    btc_qty = max_btc #btc
    max_usdt = max_usdt_bid * btc_qty / btc_usdt_bid_qty #usdt
    btc_usdt_bid_qty -= max_usdt / btc_usdt_bid_price #btc

    if btc_usdt_bid_qty == 0:
        #update price and qty
        btc_usdt_bid_qty = btc_usdt_full_book_bid_qty.pop(0)
        btc_usdt_bid_price = btc_usdt_full_book_bid_price.pop(0)

    return cash,btc_usdt_bid_qty,btc_usdt_bid_price,btc_usdt_full_book_bid_qty,btc_usdt_full_book_bid_price,eth_btc_bid_qty,eth_btc_bid_price,eth_btc_full_book_bid_qty,eth_btc_full_book_bid_price,eth_usdt_ask_qty,eth_usdt_ask_price,eth_usdt_full_book_ask_qty,eth_usdt_full_book_ask_price

def find_position_max2(btc_usdt_ask_price,btc_usdt_ask_qty,eth_btc_ask_price,eth_btc_ask_qty,eth_usdt_bid_price,eth_usdt_bid_qty,cash,fee3,eth_btc_full_book_ask_price,eth_btc_full_book_ask_qty,eth_usdt_full_book_bid_price,eth_usdt_full_book_bid_qty,btc_usdt_full_book_ask_price,btc_usdt_full_book_ask_qty):
    # step 1 : compare cash vs usdt_qty in btc_usdt

    #maximum amount of usdt on the bid side for btc_usdt
    max_usdt_bid = eth_usdt_bid_price*eth_usdt_bid_qty
    #maximum amount of usdt we can buy
    max_usdt = min(cash,max_usdt_bid)
    #maximum amount of btc that can be bought with this amount of usdt
    eth_qty = eth_usdt_bid_qty * max_usdt / max_usdt_bid


    # step 2 :  compare btc_qty vs btc qty in eth_btc
    max_eth_ask = eth_btc_ask_qty
    max_eth = min(eth_qty,max_eth_ask)
    btc_qty = eth_btc_ask_price * max_btc / max_btc_ask


    # step 3: compare eth_qty with est qty in eth_usdt
    max_btc_ask = btc_usdt_ask_qty * btc_usdt_ask_price
    max_btc = min(btc_qty,max_btc_ask)
    btc_ask_qty = btc_usdt_ask_qty * max_btc / max_btc_ask
####
    #step 4 : convert in usdt (we don't need to compare with cash)
    position_max = eth_ask_qty*eth_usdt_ask_price

    #variation of the position_max
    cash -= position_max

    position_max *= btc_usdt_bid*eth_btc_bid/eth_usdt_ask*fee3
    cash += position_max
    #to update the new bids/asks qty, we need to backpropagate the max postion
    eth_usdt_ask_qty -= max_eth
    if eth_usdt_ask_qty == 0:
        #update price from full book
        #update qty from full book
        eth_usdt_ask_qty = eth_usdt_full_book_ask_qty.pop(0)
        eth_usdt_ask_price = eth_usdt_full_book_ask_price.pop(0)

    eth_qty = max_eth
    max_btc = eth_qty * max_btc_bid / eth_btc_bid_qty

    eth_btc_bid_qty -= max_btc / eth_btc_bid_price

    if eth_btc_bid_qty == 0:
        #update price and qty
        eth_btc_bid_qty = eth_btc_full_book_bid_qty.pop(0)
        eth_btc_bid_price = eth_btc_full_book_bid_price.pop(0)

    btc_qty = max_btc
    max_usdt = max_usdt_bid * btc_qty / btc_usdt_bid_qty
    btc_usdt_bid_qty -= max_usdt / btc_usdt_bid_price

    if btc_usdt_bid_qty == 0:
        #update price and qty
        btc_usdt_bid_qty = btc_usdt_full_book_bid_qty.pop(0)
        btc_usdt_bid_price = btc_usdt_full_book_bid_price.pop(0)

    return
# Loading the data
df_btc_usdt = pd.read_csv('btcusdt_socket_book_async.csv').astype('float32')
df_eth_usdt = pd.read_csv('ethusdt_socket_book_async.csv').astype('float32')
df_eth_btc = pd.read_csv('ethbtc_socket_book_async.csv').astype('float32')


df_btc_usdt_full_book = pd.read_csv('btcusdt_socket_full_book_async.csv').astype('float32')
df_eth_usdt_full_book = pd.read_csv('ethusdt_socket_full_book_async.csv').astype('float32')
df_eth_btc_full_book = pd.read_csv('ethbtc_socket_full_book_async.csv').astype('float32')


# We add the market for each df
df_btc_usdt['market'] = 'BTCUSDT'
df_eth_usdt['market'] = 'ETHUSDT'
df_eth_btc['market'] = 'ETHBTC'

df_btc_usdt_full_book['market'] = 'BTCUSDT'
df_eth_usdt_full_book['market'] = 'ETHUSDT'
df_eth_btc_full_book['market'] = 'ETHBTC'

df_btc_usdt['book'] = 'shallow_book'
df_eth_usdt['book'] = 'shallow_book'
df_eth_btc['book'] = 'shallow_book'

df_btc_usdt_full_book['book'] = 'full_book'
df_eth_usdt_full_book['book'] = 'full_book'
df_eth_btc_full_book['book'] = 'full_book'




# We look for the lowest last timestamps amoung the 3 df
lower_max_timestamps = min(df_btc_usdt['timestamps'].iloc[-1],df_eth_usdt['timestamps'].iloc[-1],df_eth_btc['timestamps'].iloc[-1],df_btc_usdt_full_book['timestamps'].iloc[-1],df_eth_usdt_full_book['timestamps'].iloc[-1],df_eth_btc_full_book['timestamps'].iloc[-1])
higher_min_timestamps = max(df_btc_usdt['timestamps'].iloc[0],df_eth_usdt['timestamps'].iloc[0],df_eth_btc['timestamps'].iloc[0])

print(higher_min_timestamps,lower_max_timestamps)

#We merge the 3 df and sort them by ascending timestamps
df = pd.concat([df_btc_usdt,df_eth_usdt,df_eth_btc,df_btc_usdt_full_book,df_eth_usdt_full_book,df_eth_btc_full_book],ignore_index=True)
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
    if df['book'][i]=='shallow_book':
        if df['market'][i] == 'BTCUSDT' :
            btc_usdt_bid_price = df['bid_price'][i]
            btc_usdt_ask_price = df['ask_price'][i]
            btc_usdt_bid_qty = df['bid_qty'][i]
            btc_usdt_ask_qty = df['ask_qty'][i]
        elif df['market'][i] == 'ETHUSDT':
            eth_usdt_bid_price = df['bid_price'][i]
            eth_usdt_ask_price = df['ask_price'][i]
            eth_usdt_bid_qty = df['bid_qty'][i]
            eth_usdt_ask_qty = df['ask_qty'][i]
        else:
            eth_btc_bid_price = df['bid_price'][i]
            eth_btc_ask_price = df['ask_price'][i]
            eth_btc_bid_qty = df['bid_qty'][i]
            eth_btc_ask_qty = df['ask_qty'][i]
    else:
        # update the full book
        if df['market'][i] == 'BTCUSDT' :
            btc_usdt_full_book_bid_price,btc_usdt_full_book_bid_qty,btc_usdt_full_book_ask_price,btc_usdt_full_book_ask_qty = get_full_book(df,i)
        elif df['market'][i] == 'ETHUSDT':
            eth_usdt_full_book_bid_price,eth_usdt_full_book_bid_qty,eth_usdt_full_book_ask_price,eth_usdt_full_book_ask_qty = get_full_book(df,i)
        else:
            eth_btc_full_book_bid_price,eth_btc_full_book_bid_qty,eth_btc_full_book_ask_price,eth_btc_full_book_ask_qty = get_full_book(df,i)
    # if all market is found once
    if all([btc_usdt_bid_price,eth_usdt_bid_price,eth_btc_bid_price]):


        # if we can make a profit with buy btc_usdt, buy eth_btc and sell eth_usdt
        # for the v3, we change the if by a while and we will update, bids/asks as they get empty when we buy
        while btc_usdt_bid_price*fee3>eth_usdt_ask/eth_btc_bid:


            # looking for the biggest possible position with the current order book
            cash,btc_usdt_bid_qty,btc_usdt_bid_price,btc_usdt_full_book_bid_qty,btc_usdt_full_book_bid_price,eth_btc_bid_qty,eth_btc_bid_price,eth_btc_full_book_bid_qty,eth_btc_full_book_bid_price,eth_usdt_ask_qty,eth_usdt_ask_price,eth_usdt_full_book_ask_qty,eth_usdt_full_book_ask_price = find_position_max1(btc_usdt_bid_price,btc_usdt_bid_qty,eth_btc_bid_price,eth_btc_bid_qty,eth_usdt_ask_price,eth_usdt_ask_qty,cash,fee3,eth_btc_full_book_bid_price,eth_btc_full_book_bid_qty,eth_usdt_full_book_ask_price,eth_usdt_full_book_ask_qty,btc_usdt_full_book_bid_price,btc_usdt_full_book_bid_qty)#min(eth_btc_bid_qty*eth_btc_bid*btc_usdt_bid,btc_usdt_bid_qty*btc_usdt_bid,eth_usdt_ask_qty*eth_usdt_ask,eth_btc_bid_qty*eth_usdt_ask,cash)

            #keep track of when an arbitrage is possible
            arb_possible.append(i)

        # if we can make a profit with sell btc_usdt, sell eth_btc and buy eth_usdt
        while btc_usdt_ask_price<eth_usdt_bid_price/eth_btc_ask_price*fee3:
            # looking for the biggest possible position with the current order book
            cash,btc_usdt_ask_qty,btc_usdt_ask_price,btc_usdt_full_book_ask_qty,btc_usdt_full_book_ask_price,eth_btc_ask_qty,eth_btc_ask_price,eth_btc_full_book_ask_qty,eth_btc_full_book_ask_price,eth_usdt_bid_qty,eth_usdt_bid_price,eth_usdt_full_book_bid_qty,eth_usdt_full_book_bid_price = find_position_max2(btc_usdt_ask_price,btc_usdt_ask_qty,eth_btc_ask_price,eth_btc_ask_qty,eth_usdt_bid_price,eth_usdt_bid_qty,cash,fee3,eth_btc_full_book_ask_price,eth_btc_full_book_ask_qty,eth_usdt_full_book_bid_price,eth_usdt_full_book_bid_qty,btc_usdt_full_book_ask_price,btc_usdt_full_book_ask_qty)#min(eth_btc_bid_qty*eth_btc_bid*btc_usdt_bid,btc_usdt_bid_qty*btc_usdt_bid,eth_usdt_ask_qty*eth_usdt_ask,eth_btc_bid_qty*eth_usdt_ask,cash)

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
