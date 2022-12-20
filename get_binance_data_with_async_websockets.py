import websocket
import pandas as pd
import numpy as np
import json
import pprint
import time
import sys
import threading

class Client(threading.Thread):

    def __init__(self,market):
        super().__init__()
        self.market = market
        self.SOCKET = "wss://stream.binance.com:9443/ws/"+market+"@bookTicker"
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
    def on_error(self, error,E):
        print('error')
        print(E)


    # run when websocket is closed
    def on_close(self,ws):
        print("### closed ###")

    # run when websocket is initialised
    def on_open(self,ws):
        print(f'Connected to Binance {self.market}\n')

    def run(self):

        self.ws.run_forever()

class Binance(Client):
    instance_list = []
    def __init__(self,market,imax):
        super().__init__(market)
        self.df = pd.DataFrame(columns=['timestamps','bid_qty','bid_price','ask_qty','ask_price'])
        self.i = 0
        self.imax = imax
        Binance.instance_list.append(self)


    def on_message(self,ws,message):


        json_message = json.loads(message)
        #pprint.pprint(json_message)
        df_socket = pd.DataFrame({'timestamps':[time.time()],'bid_qty':[json_message['B']],'bid_price':[json_message['b']],'ask_qty':[json_message['A']],'ask_price':[json_message['a']]})

        self.df = pd.concat([self.df,df_socket],ignore_index=True)

        self.i+=1
        print(self.i)
        if self.i > self.imax:
            # self.df.to_csv(self.market+'_socket_book.csv')
            # ws.close()
            Binance.close_all()

    def on_open(self,ws):
        print('Opening connection!')



    @classmethod
    def close_all(cls):
        for self_ in Binance.instance_list:
            print(f'Closing {self_.market}')
            self_.df.to_csv(self_.market+'_socket_book_async.csv')
            self_.ws.close()
            len_df = self_.df.shape[0]
            print(f'{self_.market} closed with {len_df} data points')


if __name__ == '__main__':
    i_max = 100000
    binance_btcusdt = Binance('btcusdt',i_max)
    binance_ethusdt = Binance('ethusdt',i_max)
    binance_ethbtc = Binance('ethbtc',i_max)

    binance_btcusdt.start()
    binance_ethusdt.start()
    binance_ethbtc.start()
