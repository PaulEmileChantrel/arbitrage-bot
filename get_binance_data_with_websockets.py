import websocket
import pandas as pd
import numpy as np
import json
import pprint
import time
import sys

def web_socket_book(market):

    # Websocket link
    print(market)
    SOCKET = "wss://stream.binance.com:9443/ws/"+market+"@bookTicker"


    df = pd.DataFrame(columns=['timestamps','bid_qty','bid_price','ask_qty','ask_price'])
    i = 0
    imax = 10000 if market !='ethbtc' else 1500

    # Function called when the websocket is open
    def on_open(ws):
        print('Opening connection!')

    # Function called when the websocket is close
    def on_close(ws):
        print('Closing connection')
        nonlocal df
        df.to_csv(market+'_socket_book.csv')


    # Function called when the websocket receive a message
    def on_message(ws,message):
        #print('Message received')
        #print(message)
        nonlocal df,i,imax

        json_message = json.loads(message)
        #pprint.pprint(json_message)
        df_socket = pd.DataFrame({'timestamps':[time.time()],'bid_qty':[json_message['B']],'bid_price':[json_message['b']],'ask_qty':[json_message['A']],'ask_price':[json_message['a']]})

        df = pd.concat([df,df_socket],ignore_index=True)

        i+=1
        print(i)
        if i > imax:
            df.to_csv(market+'_socket_book.csv')
            ws.close()


    # Initialazing the websocket
    ws = websocket.WebSocketApp(SOCKET,on_open=on_open,on_close=on_close,on_message=on_message)

    # Run the web socket
    ws.run_forever()


if __name__ == '__main__':
    web_socket_book(sys.argv[1])
