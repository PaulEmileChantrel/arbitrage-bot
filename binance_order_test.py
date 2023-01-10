from config import api_key, api_secret
from binance.client import Client
from binance.enums import *
import time,math

def main():
    #starting API client
    client = Client(api_key,api_secret)

    #get the balance of USDT
    usdt_qty = client.get_asset_balance(asset='USDT')
    print(usdt_qty)


    #get btc price
    depth = client.get_order_book(symbol='BTCUSDT')
    #print(depth)

    btc_bid_price = depth['asks'][0][0]
    print('btc price :',btc_bid_price)
    #Calcul the quantity of BTC to buy
    btc_qty = float(usdt_qty['free'])/float(btc_bid_price) * 0.2
    print('btc to buy : ', round(btc_qty,5))
    depth = client.get_order_book(symbol='ETHBTC')
    #print(depth)
    eth_bid_price = depth['asks'][0][0]

    eth_qty = btc_qty/float(eth_bid_price)
    print('eth to buy : ',round(eth_qty,4))

    try:
        # We make 3 consecutive orders
        order = client.create_order(
            symbol='BTCUSDT',
            side=SIDE_BUY,
            type=ORDER_TYPE_MARKET,
            quantity=str(round(btc_qty,5)))#btc
        print('btc usdt buy success')
        #print(order)

        order = client.create_order(
            symbol='ETHBTC',
            side=SIDE_BUY,
            type=ORDER_TYPE_MARKET,
            quoteOrderQty=str(round(btc_qty,5)))#btc
        print('eth btc buy success')
        print(order)
        order = client.create_order(
            symbol='ETHUSDT',
            side=SIDE_SELL,
            type=ORDER_TYPE_MARKET,
            quantity=str(round(eth_qty,4)))

        print('eth usdt sell success')
    except :
        pass
    #get the new quantity of USDT and check if we have some btc and eth left
    usdt_qty = client.get_asset_balance(asset='USDT')
    btc_qty = client.get_asset_balance(asset='BTC')
    eth_qty = client.get_asset_balance(asset='ETH')
    print(usdt_qty)
    print(btc_qty)
    print(eth_qty)

def market_sell(client,asset):
    round_digit = 5 if asset =='BTC' else 4
    round_down = 0.5*10**-round_digit
    #Get BTC quantity in portfolio
    btc_qty = client.get_asset_balance(asset=asset)
    btc_qty = round(float(btc_qty['free'])-round_down,round_digit)

    market = asset+'USDT'

    #Sell it
    print(btc_qty)
    if btc_qty>0.0001:
        order = client.create_order(
            symbol=market,
            side=SIDE_SELL,
            type=ORDER_TYPE_MARKET,
            quantity=btc_qty)#btc
        print(f'{asset} USDT sold successfully')
    else:
        print(f'Not enough {asset} to make a sell')

    #check balance
    btc_balance = client.get_asset_balance(asset=asset)
    usdt_balance = client.get_asset_balance(asset='USDT')
    print(btc_balance)
    print(usdt_balance)

def limit_buy_btc(client):


    depth = client.get_order_book(symbol='BTCUSDT')
    #print(depth)

    btc_bid_price = float(depth['bids'][0][0]) - 0.01
    print(btc_bid_price*0.001)
    order = client.create_order(
        symbol='BTCUSDT',
        side=SIDE_BUY,
        type=ORDER_TYPE_LIMIT,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity=0.001,#qty of btc
        price=round(btc_bid_price,5))#price of btc

    print(order)
    print('')


    # check if order is filled every seconds for 20s
    order_id = order['orderId']
    filled = False
    for _ in range(20):
        order = client.get_order(
        symbol='BTCUSDT',
        orderId=order_id)
        print(order)
        print('')
        time.sleep(1)
        status = order['status']
        if status == 'FILLED':
            filled = True
            break

    #cancel order
    if not filled:
        result = client.cancel_order(
        symbol='BTCUSDT',
        orderId=order_id)
        print(result)

if __name__ =='__main__':
    client = Client(api_key,api_secret)
    #limit_buy_btc(client)
    market_sell(client,'BTC')
    market_sell(client,'ETH')
