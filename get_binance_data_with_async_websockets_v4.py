import websocket
import pandas as pd
import numpy as np
import json
import pprint
import time
import sys
import threading
#from trading_bot_v4 import *

class Client(threading.Thread):

    def __init__(self,socket):
        super().__init__()
        self.ws = websocket.WebSocketApp(
            url = self.SOCKET,
            on_message = self.on_message,
            on_error = self.on_error,
            on_close = self.on_close,
            on_open = self.on_open
        )

    # convert message to dict, process update
    def on_message(self,ws, message):
        pass

    # catch errors
    def on_error(self, ws,E):
        print('error')
        print(E)


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
    def __init__(self,market,imax):
        self.market = market
        self.SOCKET = "wss://stream.binance.com:9443/ws/"+market+"@bookTicker"

        super().__init__(self.SOCKET)
        self.df = pd.DataFrame(columns=['timestamps','bid_qty','bid_price','ask_qty','ask_price'])
        self.i = 0
        self.imax = imax
        Binance_bookTicker.instance_list.append(self)


    def on_message(self,ws,message):

        global market_dict
        json_message = json.loads(message)
        #pprint.pprint(json_message)
        market_dict[self.market] = {'bid_qty':[json_message['B']],'bid_price':[json_message['b']],'ask_qty':[json_message['A']],'ask_price':[json_message['a']]}
        pprint.pprint(market_dict)
        # We can also save the data if needed
        #df_socket = pd.DataFrame({'timestamps':[time.time()],'id':[json_message['u']],'bid_qty':[json_message['B']],'bid_price':[json_message['b']],'ask_qty':[json_message['A']],'ask_price':[json_message['a']]})
        #self.df = pd.concat([self.df,df_socket],ignore_index=True)

        self.i+=1
        print(self.i)
        if self.i > self.imax:
            # self.df.to_csv(self.market+'_socket_book.csv')
            # ws.close()
            Binance_bookTicker.close_all()
            Binance_depth.close_all()

    def on_open(self,ws):
        print('Opening connection!')



    @classmethod
    def close_all(cls):
        global market_dict

        for self_ in Binance_bookTicker.instance_list:
            print(f'Closing {self_.market}')
            #self_.df.to_csv(self_.market+'_socket_book_async.csv',index=False)
            self_.ws.close()
            len_df = self_.df.shape[0]
            print(f'{self_.market} closed with {len_df} data points')
        pprint.pprint(market_dict)

class Binance_depth(Client):
    instance_list = []
    def __init__(self,market):
        self.market = market
        self.SOCKET = "wss://stream.binance.com:9443/ws/"+market+"@depth20@100ms"

        super().__init__(self.SOCKET)
        self.df = pd.DataFrame(columns=['timestamps','id'])

        Binance_depth.instance_list.append(self)


    def on_message(self,ws,message):

        global full_book_market_dict
        json_message = json.loads(message)
        #pprint.pprint(json_message)
        # Step 1 -> update data
        # Step 2 -> make trade

        #df_socket = pd.DataFrame({'timestamps':[time.time()],'id':[json_message['lastUpdateId']]})
        full_book_market_dict[self.market] = [] #reset to the new book
        for i in range(len(json_message['bids'])):
            full_book_market_dict[self.market].append({'bid_qty':json_message['bids'][i][1],'bid_price':json_message['bids'][i][0],'ask_qty':json_message['asks'][i][1],'ask_price':json_message['asks'][i][0]})
            # bid_qty = 'bid_qty'+str(i)
            # bid_price = 'bid_price'+str(i)
            # ask_qty = 'ask_qty'+str(i)
            # ask_price = 'ask_price'+str(i)
            # df_socket[bid_price] = json_message['bids'][i][0]
            # df_socket[bid_qty] = json_message['bids'][i][1]
            # df_socket[ask_price] = json_message['asks'][i][0]
            # df_socket[ask_qty] = json_message['asks'][i][1]
        # self.df = pd.concat([self.df,df_socket],ignore_index=True)



    def on_open(self,ws):
        print('Opening connection!')

    def on_close(self,*args,**kwargs):
        Binance_bookTicker.close_all()
        Binance_depth.close_all()

    @classmethod
    def close_all(cls):
        global full_book_market_dict
        for self_ in Binance_depth.instance_list:
            print(f'Closing {self_.market}')
            #self_.df.to_csv(self_.market+'_socket_full_book_async.csv',index=False)
            self_.ws.close()
            len_df = self_.df.shape[0]
            print(f'{self_.market} full book closed with {len_df} data points')
        pprint.pprint(full_book_market_dict)

if __name__ == '__main__':
    i_max = 300

    #market = ['btcusdt','ethusdt','ethbtc']
    #global variable to keep track of shallow book data
    market_dict = {'btcusdt':None,'ethusdt':None,'ethbtc':None}
    binance_btcusdt = Binance_bookTicker('btcusdt',i_max)
    binance_ethusdt = Binance_bookTicker('ethusdt',i_max)
    binance_ethbtc = Binance_bookTicker('ethbtc',i_max)

    #global variable to keep track of shallow book data
    full_book_market_dict = {'btcusdt':None,'ethusdt':None,'ethbtc':None}

    binance_btcusdt_depth = Binance_depth('btcusdt')
    binance_ethusdt_depth = Binance_depth('ethusdt')
    binance_ethbtc_depth = Binance_depth('ethbtc')


    binance_btcusdt.start()
    binance_ethusdt.start()
    binance_ethbtc.start()

    binance_btcusdt_depth.start()
    binance_ethusdt_depth.start()
    binance_ethbtc_depth.start()
