import websocket
import pandas as pd
import numpy as np
import json
import pprint
import time

# Websocket link
SOCKET_BTC_USDT = "wss://stream.binance.com:9443/ws/btcusdt@bookTicker"
SOCKET_ETH_USDT = "wss://stream.binance.com:9443/ws/ethusdt@bookTicker"


df = pd.DataFrame(columns=['timestamps','bid_qty','bid_price','ask_qty','ask_price'])
i = 0


# Function called when the websocket is open
def on_open(ws):
    print('Opening connection!')

# Function called when the websocket is close
def on_close(ws):
    print('Closing connection')
    global df
    df.to_csv('ETHUSDT_socket_book.csv')


# Function called when the websocket receive a message
def on_message1(ws,message):
    #print('Message received')
    #print(message)
    global df,i

    json_message = json.loads(message)
    #pprint.pprint(json_message)
    df_socket = pd.DataFrame({'timestamps':[time.time()],'bid_qty':[json_message['B']],'bid_price':[json_message['b']],'ask_qty':[json_message['A']],'ask_price':[json_message['a']]})

    df = pd.concat([df,df_socket],ignore_index=True)

    i+=1
    print(i)
    if i > 10000:
        df.to_csv('BTCUSDT_socket_book.csv')
        ws.close()


# Initialazing the websocket
ws1 = websocket.WebSocketApp(SOCKET_BTC_USDT,on_open=on_open,on_close=on_close,on_message=on_message1)
ws2 = websocket.WebSocketApp(SOCKET_ETH_USDT,on_open=on_open,on_close=on_close,on_message=on_message2)

# Run the web socket
ws1.run_forever()
#,ws2.run_forever()
