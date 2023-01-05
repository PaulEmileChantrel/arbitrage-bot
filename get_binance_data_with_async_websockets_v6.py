import websocket
import pandas as pd
import numpy as np
import json
import pprint
import time
import sys
import threading
from trading_bot_v6 import TraderBot
import traceback
from binance.client import Client as API_Client
from config import api_key,api_secret


class Client(threading.Thread):

    def __init__(self,socket,bot):
        super().__init__()
        self.ws = websocket.WebSocketApp(
            url = self.SOCKET,
            on_message = self.on_message,
            on_error = self.on_error,
            on_close = self.on_close,
            on_open = self.on_open
        )
        self.bot = bot

    # convert message to dict, process update
    def on_message(self,ws, message):
        pass

    # catch errors
    def on_error(self, ws,E):
        # print('error')
        # print(E)
        traceback.print_exc()


    # run when websocket is closed
    def on_close(self,ws,*args,**kwargs):
        print("### closed ###")

    # run when websocket is initialised
    def on_open(self,ws):
        print(f'Connected to Binance {self.market}\n')

    def run(self):

        self.ws.run_forever()

class Binance_bookTicker(Client):
    instance_list = []
    def __init__(self,market,imax,bot):
        self.market = market
        self.SOCKET = "wss://stream.binance.com:9443/ws/"+market+"@bookTicker"

        super().__init__(self.SOCKET,bot)
        self.df = pd.DataFrame(columns=['timestamps','bid_qty','bid_price','ask_qty','ask_price'])
        self.i = 0
        self.imax = imax
        Binance_bookTicker.instance_list.append(self)


    def on_message(self,ws,message):

        json_message = json.loads(message)
        #pprint.pprint(json_message)
        self.bot.market_dict[self.market] = {'bid_qty':json_message['B'],'bid_price':json_message['b'],'ask_qty':json_message['A'],'ask_price':json_message['a']}

        #pprint.pprint(market_dict)
        # We can also save the data if needed
        #df_socket = pd.DataFrame({'timestamps':[time.time()],'id':[json_message['u']],'bid_qty':[json_message['B']],'bid_price':[json_message['b']],'ask_qty':[json_message['A']],'ask_price':[json_message['a']]})
        #self.df = pd.concat([self.df,df_socket],ignore_index=True)
        start_cash = self.bot.cash_tracker
        self.i+=1
        print(self.i)
        if self.i > self.imax:
            # self.df.to_csv(self.market+'_socket_book.csv')
            # ws.close()
            Binance_bookTicker.close_all()
            Binance_depth.close_all()
        self.bot.make_trade()
        #market_dict,full_book_market_dict,cash = make_trade(market_dict,full_book_market_dict,cash,client)
        if start_cash != self.bot.cash_tracker:
            Binance_bookTicker.close_all()
            Binance_depth.close_all()

    def on_open(self,ws):
        print('Opening connection!')



    @classmethod
    def close_all(cls):
        #global market_dict,cash

        for self_ in Binance_bookTicker.instance_list:
            print(f'Closing {self_.market}')
            #self_.df.to_csv(self_.market+'_socket_book_async.csv',index=False)
            self_.ws.close()
            len_df = self_.df.shape[0]
            print(f'{self_.market} closed with {len_df} data points')
        #pprint.pprint(market_dict)
        print(self.bot.cash_tracker)

class Binance_depth(Client):
    instance_list = []
    def __init__(self,market,bot):
        self.market = market
        self.SOCKET = "wss://stream.binance.com:9443/ws/"+market+"@depth20@100ms"

        super().__init__(self.SOCKET,bot)
        self.df = pd.DataFrame(columns=['timestamps','id'])

        Binance_depth.instance_list.append(self)


    def on_message(self,ws,message):


        json_message = json.loads(message)
        #pprint.pprint(json_message)
        # Step 1 -> update data
        # Step 2 -> make trade

        #df_socket = pd.DataFrame({'timestamps':[time.time()],'id':[json_message['lastUpdateId']]})

        bid_price = []
        bid_qty = []
        ask_price = []
        ask_qty = []
        start_cash = self.bot.cash_tracker
        for i in range(len(json_message['bids'])):
            bid_price.append(float(json_message['bids'][i][0]))
            bid_qty.append(float(json_message['bids'][i][1]))
            ask_price.append(float(json_message['asks'][i][0]))
            ask_qty.append(float(json_message['asks'][i][1]))


            # bid_qty = 'bid_qty'+str(i)
            # bid_price = 'bid_price'+str(i)
            # ask_qty = 'ask_qty'+str(i)
            # ask_price = 'ask_price'+str(i)
            # df_socket[bid_price] = json_message['bids'][i][0]
            # df_socket[bid_qty] = json_message['bids'][i][1]
            # df_socket[ask_price] = json_message['asks'][i][0]
            # df_socket[ask_qty] = json_message['asks'][i][1]
        # self.df = pd.concat([self.df,df_socket],ignore_index=True)

        self.bot.full_book_market_dict[self.market]={'bid_qty':bid_qty,'bid_price':bid_price,'ask_qty':ask_qty,'ask_price':ask_price}
        self.bot.make_trade()#market_dict,full_book_market_dict,cash = make_trade(self.bot.market_dict,full_book_market_dict,cash,client)
        if start_cash != self.bot.cash_tracker:
            Binance_bookTicker.close_all()
            Binance_depth.close_all()

    def on_open(self,ws):
        print('Opening connection!')

    def on_close(self,*args,**kwargs):
        Binance_bookTicker.close_all()
        Binance_depth.close_all()

    @classmethod
    def close_all(cls):
        global full_book_market_dict,cash
        for self_ in Binance_depth.instance_list:
            print(f'Closing {self_.market}')
            #self_.df.to_csv(self_.market+'_socket_full_book_async.csv',index=False)
            self_.ws.close()
            len_df = self_.df.shape[0]
            print(f'{self_.market} full book closed with {len_df} data points')
        #pprint.pprint(full_book_market_dict)
        print(self.bot.cash_tracker)

if __name__ == '__main__':
    i_max = 1000000
    start_cash = cash = 100
    market1,market2,market3 = 'btcusdt','ethbtc','ethusdt'

    #Binance API Client
    client = API_Client(api_key, api_secret)
    #variable to keep track of full book data
    market_dict = {market1:None,market2:None,market3:None}
    #variable to keep track of full book data
    full_book_market_dict = {market1:None,market2:None,market3:None}

    #trading bot
    bot = TraderBot(market1,market2,market3,cash,clent,market_dict,full_book_market_dict)

    binance_btcusdt = Binance_bookTicker(market1,i_max,bot)
    binance_ethbtc = Binance_bookTicker(market2,i_max,bot)
    binance_ethusdt = Binance_bookTicker(market3,i_max,bot)


    binance_btcusdt_depth = Binance_depth(market1,bot)
    binance_ethbtc_depth = Binance_depth(market2,bot)
    binance_ethusdt_depth = Binance_depth(market3,bot)


    binance_btcusdt.start()
    binance_ethusdt.start()
    binance_ethbtc.start()

    binance_btcusdt_depth.start()
    binance_ethusdt_depth.start()
    binance_ethbtc_depth.start()
