import pandas as pd
import numpy as np
import pprint
from config import api_key, api_secret
from binance.client import Client
from binance.enums import *
#from binance.exceptions.BinanceAPIException import *
import threading
import time

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
        self.order_id1 = None
        self.order_id2 = None
        self.limit_order_thread1 = None
        self.limit_order_thread2 = None
        self.executed_qty1 = 0
        self.executed_qty2 = 0
        real_cash = self.binance_client.get_asset_balance(asset='USDT')#Warning -> this shoudn't be hardcoded
        self.real_cash = float(real_cash['free'])
        self.available_cash = float(real_cash['free'])
        # trading fee
        self.fee = 0.00075 #0.01 = 1%
        # fees multiplier for 3 transactions
        self.fee3 = (1-self.fee)**2
        self.first_run = True
        self.need_to_stop = False

    def market_sell1(self):
        #This function is called when the Btc order get filled or partially filled
        # It will market buy ETHBTC and market sell ETHUSDT

        print(f'Market selling ETHBTC -> ETHUSDT')
        round_down5 = 0.5*10**-5
        round_down4 = 0.5*10**-4
        btc_qty = round(self.executed_qty1-round_down5,5)

        #btc_balance = self.binance_client.get_asset_balance(asset='BTC')
        print(btc_qty)
        #print(btc_balance)
        if btc_qty >0.00001:
            order = self.binance_client.create_order(
                symbol='ETHBTC',
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quoteOrderQty=str(btc_qty))#btc
            print('eth btc buy success')
            print(order)
            eth_qty = float(order['executedQty'])
            order = self.binance_client.create_order(
                symbol='ETHUSDT',
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=str(round(eth_qty,4)))

            print('eth usdt sell success')
        else:
            print('not enough BTC')
        usdt_balance = self.binance_client.get_asset_balance(asset='USDT')
        usdt_balance = float(usdt_balance['free'])
        self.need_to_stop = self.real_cash>usdt_balance and self.real_cash*0.9<usdt_balance #usdt balance is lower than before but not too low
        print(f'USDT before : {self.real_cash}, USDT after full trade: {usdt_balance}, Need to stop ? -> {self.need_to_stop}')


    def update_limit_order1(self,order_price,order_size):
        order_id = self.order_id1

        #cancel previous order
        if order_id:
            try:
                print(f'trying to cancel order {order_id}')
                result = self.binance_client.cancel_order(
                    symbol=self.market1.upper(),
                    orderId=order_id)
                print(f'order {order_id} cancelled')
            except:
                #try to cancel but the order just got filled
                #market sell it
                print(f'order {order_id} was actually filled')
                #Since the order has been filled, we need to update self.executed_qty1
                self.executed_qty1 = self.order_size1 - self.executed_qty1
                self.market_sell1()
                return #We dont place a new order
        self.order_id1 = None
        print(order_size,order_price, round(order_size,5)*order_price)


        #add new order
        try:
            order = self.binance_client.create_order(
                symbol=self.market1.upper(),
                side=SIDE_BUY,
                type=ORDER_TYPE_LIMIT,
                timeInForce=TIME_IN_FORCE_GTC,
                quantity=round(order_size,5),
                price=round(order_price,2))
        except :
            print('Api error, order not placed')
        else:
            self.order_size1 = round(order_size,5)
            self.order_id1 = order['orderId']
            usdt_balance = self.binance_client.get_asset_balance(asset='USDT')
            self.available_cash = float(usdt_balance['free'])
            #close old thread of check_limit_filled
            if self.limit_order_thread1:
                self.limit_order_thread1.stop()


            #open new one
            self.limit_order_thread1 = threading.Thread(target=self.check_limit_filled1,args=())
            self.limit_order_thread1.start()

    def check_limit_filled1(self):
        # if market == self.market1:
        #     order_id = self.order_id1
        # else:
        #     order_id = self.order_id2
        order_id = self.order_id1
        self.executed_qty1 = 0
        #check every x seconds
        while True and order_id:
            time.sleep(0.4)
            print(f'checking {order_id} status')
            order = self.binance_client.get_order(
                symbol='BTCUSDT',
                orderId=order_id)
            status = order['status']
            print('order status : ',status)
            self.executed_qty1 = float(order['executedQty'])-self.executed_qty1#if its partially filled, we call the market sell function anyway
            self.market_sell1()

            if status == 'FILLED':
                filled = True
                break

    def get_order_size1(self,final_order):


        #btc size (in btc) #cash available / btc_price
        btc_max = self.real_cash/final_order

        eth_btc_bid_price = float(self.market_dict[self.market2]['bid_price'])
        eth_btc_bid_qty = float(self.market_dict[self.market2]['bid_qty'])
        eth_qty = btc_max/eth_btc_bid_price #qty I can buy with btc_max
        eth_max = min(eth_qty,eth_btc_bid_qty) #max qty I can buy

        eth_usdt_bid_price = float(self.market_dict[self.market3]['bid_price'])
        eth_usdt_bid_qty = float(self.market_dict[self.market3]['bid_qty'])
        eth_max = min(eth_max,eth_usdt_bid_qty) #max qty of eth I can sell

        usdt_max = eth_max*eth_usdt_bid_price

        final_btc_size = usdt_max/final_order

        return final_btc_size

    def place_limit_order1(self):

        #1)check previous limit order
        past_order = self.limit_order_price1

        #2) calcul new limit order

        eth_usdt_ask_price = float(self.market_dict[self.market3]['ask_price'])
        eth_btc_bid_price = float(self.market_dict[self.market2]['bid_price'])

        new_order = eth_usdt_ask_price/eth_btc_bid_price/self.fee3 #approx btc price
        safety = 0.00

        new_order-=safety
        new_order = round(new_order,2)

        #3) Select the new order we will put knowing.
        # we have 2 values to compare

        #rule : -> I dont want to put a loosing order (with the next market buy)
        #It means that I just need to update previous order to new order wether it's higher or lower
        #If its the same, I wont update my limi order
        # We don't care the btcusdt ask or bid since we will make money no matter what with this rule
        if past_order == new_order:
            final_order = None
        else:
            final_order = new_order

        if final_order:
            order_size = self.get_order_size1(final_order)
            self.update_limit_order1(final_order,order_size)

    def make_trade(self):
        #Make a trade if possible

        start_cash = self.cash_tracker

        try:

            eth_usdt_bid_price = float(self.market_dict[self.market3]['bid_price'])
            eth_usdt_ask_price = float(self.market_dict[self.market3]['ask_price'])
            eth_usdt_bid_qty = float(self.market_dict[self.market3]['bid_qty'])
            eth_usdt_ask_qty = float(self.market_dict[self.market3]['ask_qty'])

            eth_btc_bid_price = float(self.market_dict[self.market2]['bid_price'])
            eth_btc_ask_price = float(self.market_dict[self.market2]['ask_price'])
            eth_btc_bid_qty = float(self.market_dict[self.market2]['bid_qty'])
            eth_btc_ask_qty = float(self.market_dict[self.market2]['ask_qty'])
            #print(full_book_market_dict['ethusdt'])

        except:
            pass
            print('Missing data')
        else:
            # if all market is found once
            print(all([eth_usdt_bid_price,eth_btc_bid_price]))
            if all([eth_usdt_bid_price,eth_btc_bid_price]):
                if self.first_run:
                    self.first_run = False
                    print("Starting trading")
                ## Instead of checking if we can make a trade, we will check the limit price for btcusdt (and eth usdt) where we can make money with ethbtc->ethusdt (and ethbtc-> btcusdt)
                ## Every time the shallow_book is updated, we update our limit order
                ## When a limit order is filled, we market sell back to usdt

                #btcusdt
                self.place_limit_order1()

                #ethusdt
                #self.place_limit_order2()

                #add changes to dictionaries

            if start_cash<self.cash_tracker:
                print(self.cash_tracker)
            #return market_dict,full_book_market_dict,cash
