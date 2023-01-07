import pandas as pd
import numpy as np
import pprint
from config import api_key, api_secret
from binance.client import Client
from binance.enums import *


class TraderBot:
    epsilon = 10**-12
    def __init__(self,market1,market2,market3,cash_tracker,market_dict,full_book_market_dict):
        self.market1 = market1
        self.market2 = market2
        self.market3 = market3
        self.cash_tracker = cash_tracker
        self.binance_client = Client(api_key,api_secret)
        self.market_dict = market_dict
        self.full_book_market_dict = full_book_market_dict
        self.limit_order_price1 = None
        self.limit_order_price2 = None
        # trading fee
        self.fee = 0.00075 #0.01 = 1%
        # fees multiplier for 3 transactions
        self.fee3 = (1-self.fee)**2

    def get_full_book(self,full_book_market_dict,market):
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

    def update_full_book(self,sub_full_book_market_dict,bid_price,bid_qty,ask_price,ask_qty):
        sub_full_book_market_dict['bid_price'] = bid_price
        sub_full_book_market_dict['bid_qty'] = bid_qty
        sub_full_book_market_dict['ask_price'] = ask_price
        sub_full_book_market_dict['ask_qty'] = ask_qty
        return sub_full_book_market_dict

    def find_position_max1(self,btc_usdt_bid_price,btc_usdt_bid_qty,eth_btc_bid_price,eth_btc_bid_qty,eth_usdt_ask_price,eth_usdt_ask_qty,cash,fee3,eth_btc_full_book_bid_price,eth_btc_full_book_bid_qty,eth_usdt_full_book_ask_price,eth_usdt_full_book_ask_qty,btc_usdt_full_book_bid_price,btc_usdt_full_book_bid_qty,client):
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
        print(round(position_max,8),round(max_btc,8),round(max_eth,8))
        print('order0')
        # info = client.get_symbol_info('BTCUSDT')
        # print(info)
        # info = client.get_symbol_info('ETHBTC')
        # print(info)
        # info = client.get_symbol_info('ETHUSDT')
        # print(info)
        order = client.create_order(
            symbol='BTCUSDT',
            side=SIDE_BUY,
            type=ORDER_TYPE_MARKET,
            quantity=str(round(max_btc,5)))#btc
        #orders = client.get_all_orders(symbol='BTCUSDT')
        print(orders)
        order = client.create_order(
            symbol='ETHBTC',
            side=SIDE_BUY,
            type=ORDER_TYPE_MARKET,
            quoteOrderQty=str(round(max_btc,5)))#btc

        order = client.create_order(
            symbol='ETHUSDT',
            side=SIDE_SELL,
            type=ORDER_TYPE_MARKET,
            quantity=str(round(max_eth,4)))
        real_cash = client.get_asset_balance(asset='USDT')
        print(real_cash)
        #variation of the position_max
        cash -= position_max
        print(btc_usdt_bid_price*eth_btc_bid_price/eth_usdt_ask_price*fee3)
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

    def find_position_max2(self,btc_usdt_ask_price,btc_usdt_ask_qty,eth_btc_ask_price,eth_btc_ask_qty,eth_usdt_bid_price,eth_usdt_bid_qty,cash,fee3,eth_btc_full_book_ask_price,eth_btc_full_book_ask_qty,eth_usdt_full_book_bid_price,eth_usdt_full_book_bid_qty,btc_usdt_full_book_ask_price,btc_usdt_full_book_ask_qty,client):

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
        print(position_max,max_eth,max_btc)
        order = client.create_order(
            symbol='ETHUSDT',
            side=SIDE_BUY,
            type=ORDER_TYPE_MARKET,
            quantity=round(max_eth,4))#eth
        print(order)
        order = client.create_order(
            symbol='ETHBTC',
            side=SIDE_SELL,
            type=ORDER_TYPE_MARKET,
            quantity=round(max_eth,4))#eth

        order = client.create_order(
            symbol='BTCUSDT',
            side=SIDE_SELL,
            type=ORDER_TYPE_MARKET,
            quantity=round(max_btc,5))#btc
        print(order)
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
    def update_limit_order1(self,order_price):
        pass
    def check_limit_filled(self,market):
        pass
    def place_limit_order1(self):


        #1)check previous limit order
        past_order = self.limit_order_price1

        #2) calcul new limit order

        eth_usdt_ask_price = self.market_dict[self.market3]['ask_price']
        eth_btc_bid_price = self.market_dict[self.market2]['bid_price']

        new_order = eth_usdt_ask_price/eth_btc_bid_price/self.fee3
        safety = 0.00001

        new_order-=safety
        new_order = round(new_order,5)

        #3) Select the new order we will put knowing.
        # we have 2 values to compare

        #rule : -> I dont want to put a loosing order (with the next market buy)
        #It means that I just need to update previous order to new order wether it's higher or lower
        #If its the same, I wont update my limi order
        # We don't care the btcusdt ask or bid since we will make money no matter what with this rule
        if previous_order == new_order:
            final_order = None
        else:
            final_order = new_order

        if final_order:
            self.update_limit_order1(final_order)



    def make_trade(self):
        #Make a trade if possible

        start_cash = self.cash_tracker


        btc_usdt_bid_price = float(self.market_dict[self.market1]['bid_price'])
        btc_usdt_ask_price = float(self.market_dict[self.market1]['ask_price'])
        btc_usdt_bid_qty = float(self.market_dict[self.market1]['bid_qty'])
        btc_usdt_ask_qty = float(self.market_dict[self.market1]['ask_qty'])

        eth_usdt_bid_price = float(self.market_dict[self.market3]['bid_price'])
        eth_usdt_ask_price = float(self.market_dict[self.market3]['ask_price'])
        eth_usdt_bid_qty = float(self.market_dict[self.market3]['bid_qty'])
        eth_usdt_ask_qty = float(self.market_dict[self.market3]['ask_qty'])

        eth_btc_bid_price = float(self.market_dict[self.market2]['bid_price'])
        eth_btc_ask_price = float(self.market_dict[self.market2]['ask_price'])
        eth_btc_bid_qty = float(self.market_dict[self.market2]['bid_qty'])
        eth_btc_ask_qty = float(self.market_dict[self.market2]['ask_qty'])
        #print(full_book_market_dict['ethusdt'])

        btc_usdt_full_book_bid_price,btc_usdt_full_book_bid_qty,btc_usdt_full_book_ask_price,btc_usdt_full_book_ask_qty = self.get_full_book(self.full_book_market_dict,self.market1)
        eth_usdt_full_book_bid_price,eth_usdt_full_book_bid_qty,eth_usdt_full_book_ask_price,eth_usdt_full_book_ask_qty = self.get_full_book(self.full_book_market_dict,self.market3)
        eth_btc_full_book_bid_price,eth_btc_full_book_bid_qty,eth_btc_full_book_ask_price,eth_btc_full_book_ask_qty = self.get_full_book(self.full_book_market_dict,self.market2)

        #print(eth_usdt_full_book_bid_qty)
        # if all market is found once
        if all([btc_usdt_bid_price,eth_usdt_bid_price,eth_btc_bid_price])and all([btc_usdt_full_book_bid_price,eth_usdt_full_book_bid_price,eth_btc_full_book_bid_price]):

            ## Instead of checking if we can make a trade, we will check the limit price for btcusdt (and eth usdt) where we can make money with ethbtc->ethusdt (and ethbtc-> btcusdt)
            ## Every time the shallow_book is updated, we update our limit order
            ## When a limit order is filled, we market sell back to usdt

            #btcusdt
            self.place_limit_order1()

            #ethusdt
            #self.place_limit_order2()

            #add changes to dictionaries

            self.market_dict[self.market1]['bid_price'] = btc_usdt_bid_price
            self.market_dict[self.market1]['ask_price'] = btc_usdt_ask_price
            self.market_dict[self.market1]['bid_qty'] = btc_usdt_bid_qty
            self.market_dict[self.market1]['ask_qty'] = btc_usdt_ask_qty

            self.market_dict[self.market3]['bid_price'] = eth_usdt_bid_price
            self.market_dict[self.market3]['ask_price'] = eth_usdt_ask_price
            self.market_dict[self.market3]['bid_qty'] = eth_usdt_bid_qty
            self.market_dict[self.market3]['ask_qty'] = eth_usdt_ask_qty

            self.market_dict[self.market2]['bid_price'] = eth_btc_bid_price
            self.market_dict[self.market2]['ask_price'] = eth_btc_ask_price
            self.market_dict[self.market2]['bid_qty'] = eth_btc_bid_qty
            self.market_dict[self.market2]['ask_qty'] = eth_btc_ask_qty

            # update full_book

            self.full_book_market_dict[self.market1] = self.update_full_book(self.full_book_market_dict[self.market1],btc_usdt_full_book_bid_price,btc_usdt_full_book_bid_qty,btc_usdt_full_book_ask_price,btc_usdt_full_book_ask_qty)
            self.full_book_market_dict[self.market3] = self.update_full_book(self.full_book_market_dict[self.market3],eth_usdt_full_book_bid_price,eth_usdt_full_book_bid_qty,eth_usdt_full_book_ask_price,eth_usdt_full_book_ask_qty)
            self.full_book_market_dict[self.market2] = self.update_full_book(self.full_book_market_dict[self.market2],eth_btc_full_book_bid_price,eth_btc_full_book_bid_qty,eth_btc_full_book_ask_price,eth_btc_full_book_ask_qty)
        if start_cash<self.cash_tracker:
            print(self.cash_tracker)
        #return market_dict,full_book_market_dict,cash



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