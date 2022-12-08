import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Loading the csv files
df_btc_usdt = pd.read_csv('BTCUSDT_ohlcv_binance_minutes.csv',index_col=[0])
df_eth_usdt = pd.read_csv('ETHUSDT_ohlcv_binance_minutes.csv',index_col=[0])
df_eth_btc = pd.read_csv('ETHBTC_ohlcv_binance_minutes.csv',index_col=[0])

# Changing the dataframes into np arrays
np_btc_usdt = df_btc_usdt.to_numpy()
np_eth_usdt = df_eth_usdt.to_numpy()
np_eth_btc = df_eth_btc.to_numpy()

print(np_btc_usdt.shape)
print(np_eth_usdt.shape)
print(np_eth_btc.shape)

# Initial cash position
cash = 1000000

# trading fee
fee = 0.001 # 0.01 => 1% fee

# fee multiplicator for three transactions
fee3 = (1-fee)**3

# Cash position through time
cash_time = [cash]

# Going through the array to look for arbitrage opportunity
for i in range(np_btc_usdt.shape[0]):

    # close price
    btc_usdt = np_btc_usdt[i,3]
    eth_usdt = np_eth_usdt[i,3]
    eth_btc = np_eth_btc[i,3]

    # buy btc_usdt then buy eth_btc then sell eth_usdt
    # if you can make money (with the fees)
    if btc_usdt*fee3 > eth_usdt/eth_btc:
        cash *= btc_usdt*fee3*eth_btc/eth_usdt

    # buy eth_usdt then sell eth_btc then sell btc_usdt
    # if you can make money (with the fees)
    elif btc_usdt < eth_usdt/eth_btc*fee3:
        cash *= eth_usdt/eth_btc/btc_usdt*fee3

    # The cash position array is updated for every minutes
    cash_time.append(cash)


# Final cash position
print(cash)

# This algorythm is good but arbitrage does not work like that in real life
# We have to take into account the spread between the bid and ask side

cash_time = np.array(cash_time)/1000000
time_day = np.array(range(len(cash_time)))/60/24


# We plot the cash position through time
plt.plot(time_day,cash_time)
plt.title("Evolution of the cash position")
plt.xlabel("Time (day)")
plt.ylabel("Cash ($M)")

plt.show()
