from config import api_key, api_secret
from binance.client import Client
from binance.enums import *


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

if __name__ =='__main__':
    main()
