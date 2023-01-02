import pandas as pd
import numpy as np
import pprint

def get_full_book(full_book_market_dict,market):
    #pprint.pprint(full_book_market_dict)
    book = full_book_market_dict[market].copy()
    #pprint.pprint(book)
    if book is None:
        return None,None,None,None
    bid_price = book['bid_price']
    bid_qty = book['bid_qty']
    ask_price = book['ask_price']
    ask_qty = book['ask_qty']

    return bid_price,bid_qty,ask_price,ask_qty

def update_full_book(sub_full_book_market_dict,bid_price,bid_qty,ask_price,ask_qty):
    sub_full_book_market_dict['bid_price'] = bid_price
    sub_full_book_market_dict['bid_qty'] = bid_qty
    sub_full_book_market_dict['ask_price'] = ask_price
    sub_full_book_market_dict['ask_qty'] = ask_qty
    return sub_full_book_market_dict

def find_position_max1(btc_usdt_bid_price,btc_usdt_bid_qty,eth_btc_bid_price,eth_btc_bid_qty,eth_usdt_ask_price,eth_usdt_ask_qty,cash,fee3,eth_btc_full_book_bid_price,eth_btc_full_book_bid_qty,eth_usdt_full_book_ask_price,eth_usdt_full_book_ask_qty,btc_usdt_full_book_bid_price,btc_usdt_full_book_bid_qty):
    #return the biggest cash position we can take on a trade
    # we have 3 trades cash-> btc, btc->eth, eth-> cash


    # step 1 : compare cash vs usdt_qty in btc_usdt

    #maximum amount of usdt on the bid side for btc_usdt
    #print(btc_usdt_bid_price,btc_usdt_bid_qty,eth_btc_bid_price,eth_usdt_ask_price)
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
    max_eth = min(eth_qty,max_eth_ask) #eth
    eth_ask_qty = max_eth   #eth

    #step 4 : convert in usdt (we don't need to compare with cash)
    position_max = eth_ask_qty*eth_usdt_ask_price #usdt

    #variation of the position_max
    cash -= position_max

    position_max *= btc_usdt_bid_price*eth_btc_bid_price/eth_usdt_ask_price*fee3
    cash += position_max

    #to update the new bids/asks qty, we need to backpropagate the max postion
    eth_usdt_ask_qty -= max_eth

    if eth_usdt_ask_qty <= epsilon and eth_usdt_full_book_ask_qty!=[]:
        #update price from full book
        #update qty from full book
        eth_usdt_ask_qty = eth_usdt_full_book_ask_qty.pop(0)
        eth_usdt_ask_price = eth_usdt_full_book_ask_price.pop(0)
    elif eth_usdt_full_book_ask_qty==[]:
        eth_usdt_ask_price = float('infinity')
    eth_qty = max_eth #eth
    max_btc = eth_qty * max_btc_bid / eth_btc_bid_qty #btc

    eth_btc_bid_qty -= max_btc / eth_btc_bid_price #eth

    if eth_btc_bid_qty <= epsilon and eth_btc_full_book_bid_qty!=[]:
        #update price and qty
        eth_btc_bid_qty = eth_btc_full_book_bid_qty.pop(0)
        eth_btc_bid_price = eth_btc_full_book_bid_price.pop(0)
    elif eth_btc_full_book_bid_qty==[]:
        eth_btc_bid_price = 10**-15
    btc_qty = max_btc #btc
    max_usdt = max_usdt_bid * btc_qty / btc_usdt_bid_qty #usdt
    btc_usdt_bid_qty -= max_usdt / btc_usdt_bid_price #btc

    if btc_usdt_bid_qty <= epsilon and btc_usdt_full_book_bid_qty!=[]:
        #update price and qty
        btc_usdt_bid_qty = btc_usdt_full_book_bid_qty.pop(0)
        btc_usdt_bid_price = btc_usdt_full_book_bid_price.pop(0)
    elif btc_usdt_full_book_bid_qty==[]:
        btc_usdt_bid_price = float('-infinity')
    return cash,btc_usdt_bid_qty,btc_usdt_bid_price,btc_usdt_full_book_bid_qty,btc_usdt_full_book_bid_price,eth_btc_bid_qty,eth_btc_bid_price,eth_btc_full_book_bid_qty,eth_btc_full_book_bid_price,eth_usdt_ask_qty,eth_usdt_ask_price,eth_usdt_full_book_ask_qty,eth_usdt_full_book_ask_price

def find_position_max2(btc_usdt_ask_price,btc_usdt_ask_qty,eth_btc_ask_price,eth_btc_ask_qty,eth_usdt_bid_price,eth_usdt_bid_qty,cash,fee3,eth_btc_full_book_ask_price,eth_btc_full_book_ask_qty,eth_usdt_full_book_bid_price,eth_usdt_full_book_bid_qty,btc_usdt_full_book_ask_price,btc_usdt_full_book_ask_qty):

    # similar but reverse
    # step 1 : compare cash vs usdt_qty in btc_usdt

    #maximum amount of usdt on the bid side for btc_usdt
    max_usdt_bid = eth_usdt_bid_price*eth_usdt_bid_qty #usdt
    #maximum amount of usdt we can buy
    max_usdt = min(cash,max_usdt_bid)   #usdt
    #maximum amount of btc that can be bought with this amount of usdt
    eth_qty = eth_usdt_bid_qty * max_usdt / max_usdt_bid #eth


    # step 2 :  compare btc_qty vs btc qty in eth_btc
    max_eth_ask = eth_btc_ask_qty  #eth
    max_eth = min(eth_qty,max_eth_ask) #eth
    btc_qty = eth_btc_ask_price * max_eth  #btc


    # step 3: compare eth_qty with est qty in eth_usdt
    max_btc_ask = btc_usdt_ask_qty # btc
    max_btc = min(btc_qty,max_btc_ask) #btc
    btc_ask_qty = max_btc #btc

    #step 4 : convert in usdt (we don't need to compare with cash)
    position_max = btc_ask_qty*btc_usdt_ask_price

    #variation of the position_max
    cash -= position_max

    position_max *= eth_usdt_bid_price/(btc_usdt_ask_price*eth_btc_ask_price)*fee3
    cash += position_max


    #to update the new bids/asks qty, we need to backpropagate the max postion
    btc_usdt_ask_qty -= max_btc
    #print(btc_usdt_full_book_ask_price)
    if btc_usdt_ask_qty <= epsilon and btc_usdt_full_book_ask_qty!=[]:
        #update price from full book
        #update qty from full book
        btc_usdt_ask_qty = btc_usdt_full_book_ask_qty.pop(0)
        btc_usdt_ask_price = btc_usdt_full_book_ask_price.pop(0)
    elif btc_usdt_full_book_ask_qty==[]:
        btc_usdt_ask_price = float('infinity')
    max_eth = max_btc / eth_btc_ask_price
    eth_btc_ask_qty -= max_eth

    if eth_btc_ask_qty <= epsilon and eth_btc_full_book_ask_qty!=[]:
        #update price and qty
        eth_btc_ask_qty = eth_btc_full_book_ask_qty.pop(0)
        eth_btc_ask_price = eth_btc_full_book_ask_price.pop(0)
    elif eth_btc_full_book_ask_qty==[]:
        eth_btc_ask_price = float('-infinity')
    #max_usdt = max_eth * max_usdt_bid / eth_usdt_bid_qty
    eth_usdt_bid_qty -= max_eth

    if eth_usdt_bid_qty <= epsilon and eth_usdt_full_book_bid_qty!=[]:
        #update price and qty
        eth_usdt_bid_qty = eth_usdt_full_book_bid_qty.pop(0)
        eth_usdt_bid_price = eth_usdt_full_book_bid_price.pop(0)
    elif eth_usdt_full_book_bid_price==[]:
        eth_usdt_bid_price = -1
    return cash,btc_usdt_ask_qty,btc_usdt_ask_price,btc_usdt_full_book_ask_qty,btc_usdt_full_book_ask_price,eth_btc_ask_qty,eth_btc_ask_price,eth_btc_full_book_ask_qty,eth_btc_full_book_ask_price,eth_usdt_bid_qty,eth_usdt_bid_price,eth_usdt_full_book_bid_qty,eth_usdt_full_book_bid_price
epsilon = 10**-12
def make_trade(market_dict,full_book_market_dict,cash):
    #Make a trade if possible

    start_cash = cash
    # trading fee
    fee = 0.001 #0.01 = 1%

    # fees multiplier for 3 transactions
    fee3 = (1-fee)**3

    btc_usdt_bid_price = float(market_dict['btcusdt']['bid_price'])
    btc_usdt_ask_price = float(market_dict['btcusdt']['ask_price'])
    btc_usdt_bid_qty = float(market_dict['btcusdt']['bid_qty'])
    btc_usdt_ask_qty = float(market_dict['btcusdt']['ask_qty'])

    eth_usdt_bid_price = float(market_dict['ethusdt']['bid_price'])
    eth_usdt_ask_price = float(market_dict['ethusdt']['ask_price'])
    eth_usdt_bid_qty = float(market_dict['ethusdt']['bid_qty'])
    eth_usdt_ask_qty = float(market_dict['ethusdt']['ask_qty'])

    eth_btc_bid_price = float(market_dict['ethbtc']['bid_price'])
    eth_btc_ask_price = float(market_dict['ethbtc']['ask_price'])
    eth_btc_bid_qty = float(market_dict['ethbtc']['bid_qty'])
    eth_btc_ask_qty = float(market_dict['ethbtc']['ask_qty'])
    #print(full_book_market_dict['ethusdt'])

    btc_usdt_full_book_bid_price,btc_usdt_full_book_bid_qty,btc_usdt_full_book_ask_price,btc_usdt_full_book_ask_qty = get_full_book(full_book_market_dict,'btcusdt')
    eth_usdt_full_book_bid_price,eth_usdt_full_book_bid_qty,eth_usdt_full_book_ask_price,eth_usdt_full_book_ask_qty = get_full_book(full_book_market_dict,'ethusdt')
    eth_btc_full_book_bid_price,eth_btc_full_book_bid_qty,eth_btc_full_book_ask_price,eth_btc_full_book_ask_qty = get_full_book(full_book_market_dict,'ethbtc')

    #print(eth_usdt_full_book_bid_qty)
    # if all market is found once
    if all([btc_usdt_bid_price,eth_usdt_bid_price,eth_btc_bid_price])and all([btc_usdt_full_book_bid_price,eth_usdt_full_book_bid_price,eth_btc_full_book_bid_price]):

        # if we can make a profit with buy btc_usdt, buy eth_btc and sell eth_usdt
        # for the v3, we change the if by a while and we will update, bids/asks as they get empty when we buy
        while btc_usdt_bid_price*fee3>eth_usdt_ask_price/eth_btc_bid_price:

            # looking for the biggest possible position with the current order book
            cash,btc_usdt_bid_qty,btc_usdt_bid_price,btc_usdt_full_book_bid_qty,btc_usdt_full_book_bid_price,eth_btc_bid_qty,eth_btc_bid_price,eth_btc_full_book_bid_qty,eth_btc_full_book_bid_price,eth_usdt_ask_qty,eth_usdt_ask_price,eth_usdt_full_book_ask_qty,eth_usdt_full_book_ask_price = find_position_max1(btc_usdt_bid_price,btc_usdt_bid_qty,eth_btc_bid_price,eth_btc_bid_qty,eth_usdt_ask_price,eth_usdt_ask_qty,cash,fee3,eth_btc_full_book_bid_price,eth_btc_full_book_bid_qty,eth_usdt_full_book_ask_price,eth_usdt_full_book_ask_qty,btc_usdt_full_book_bid_price,btc_usdt_full_book_bid_qty)#min(eth_btc_bid_qty*eth_btc_bid*btc_usdt_bid,btc_usdt_bid_qty*btc_usdt_bid,eth_usdt_ask_qty*eth_usdt_ask,eth_btc_bid_qty*eth_usdt_ask,cash)

        # if we can make a profit with sell btc_usdt, sell eth_btc and buy eth_usdt
        while btc_usdt_ask_price<eth_usdt_bid_price/eth_btc_ask_price*fee3:
            # looking for the biggest possible position with the current order book
            cash,btc_usdt_ask_qty,btc_usdt_ask_price,btc_usdt_full_book_ask_qty,btc_usdt_full_book_ask_price,eth_btc_ask_qty,eth_btc_ask_price,eth_btc_full_book_ask_qty,eth_btc_full_book_ask_price,eth_usdt_bid_qty,eth_usdt_bid_price,eth_usdt_full_book_bid_qty,eth_usdt_full_book_bid_price = find_position_max2(btc_usdt_ask_price,btc_usdt_ask_qty,eth_btc_ask_price,eth_btc_ask_qty,eth_usdt_bid_price,eth_usdt_bid_qty,cash,fee3,eth_btc_full_book_ask_price,eth_btc_full_book_ask_qty,eth_usdt_full_book_bid_price,eth_usdt_full_book_bid_qty,btc_usdt_full_book_ask_price,btc_usdt_full_book_ask_qty)#min(eth_btc_bid_qty*eth_btc_bid*btc_usdt_bid,btc_usdt_bid_qty*btc_usdt_bid,eth_usdt_ask_qty*eth_usdt_ask,eth_btc_bid_qty*eth_usdt_ask,cash)

        #add changes to dictionaries

        market_dict['btcusdt']['bid_price'] = btc_usdt_bid_price
        market_dict['btcusdt']['ask_price'] = btc_usdt_ask_price
        market_dict['btcusdt']['bid_qty'] = btc_usdt_bid_qty
        market_dict['btcusdt']['ask_qty'] = btc_usdt_ask_qty

        market_dict['ethusdt']['bid_price'] = eth_usdt_bid_price
        market_dict['ethusdt']['ask_price'] = eth_usdt_ask_price
        market_dict['ethusdt']['bid_qty'] = eth_usdt_bid_qty
        market_dict['ethusdt']['ask_qty'] = eth_usdt_ask_qty

        market_dict['ethbtc']['bid_price'] = eth_btc_bid_price
        market_dict['ethbtc']['ask_price'] = eth_btc_ask_price
        market_dict['ethbtc']['bid_qty'] = eth_btc_bid_qty
        market_dict['ethbtc']['ask_qty'] = eth_btc_ask_qty

        # update full_book

        full_book_market_dict['btcusdt'] = update_full_book(full_book_market_dict['btcusdt'],btc_usdt_full_book_bid_price,btc_usdt_full_book_bid_qty,btc_usdt_full_book_ask_price,btc_usdt_full_book_ask_qty)
        full_book_market_dict['ethusdt'] = update_full_book(full_book_market_dict['ethusdt'],eth_usdt_full_book_bid_price,eth_usdt_full_book_bid_qty,eth_usdt_full_book_ask_price,eth_usdt_full_book_ask_qty)
        full_book_market_dict['ethbtc'] = update_full_book(full_book_market_dict['ethbtc'],eth_btc_full_book_bid_price,eth_btc_full_book_bid_qty,eth_btc_full_book_ask_price,eth_btc_full_book_ask_qty)
    if start_cash<=cash:
        print(cash)
    return market_dict,full_book_market_dict,cash



# #print(arb_possible)
# print(cash)
# print(len(arb_possible))
# print(len(cash_time))
# print((cash/start_cash-1)*100)
# cash_time = np.array(cash_time)-start_cash
#
# import matplotlib.pyplot as plt
# plt.plot(cash_time)
# plt.title("Evolution of the cash position")
# plt.xlabel("Time")
# plt.ylabel("Cash ($)")
#
# plt.show()
