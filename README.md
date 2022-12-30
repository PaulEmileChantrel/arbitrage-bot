# Arbitrage bot

In this project, we create an arbitrage bot.


### Version 1
For the first version, we download OHLCV minutes data for BTC/USDT, ETH/USDT and ETH/BTC on Binance.

Then, we go through the data and only make a transaction when we can buy BTC/USDT, then buy ETH/USDT, and then sell ETH/UDST and be profitable with fees or when we can buy ETH/USDT, sell ETH/BTC and sell BTC/USDT and be profitable with fees.

We are able to go from $1,000,000 to $3,208,288 with the data going from Feb. 9, 2018 to Dec. 7 2022.

<p align='center'>
<img src='https://user-images.githubusercontent.com/96018383/206340771-15e335f6-f8f3-405d-aa1e-e1b9a3918592.png'>

</p>

This algorythm is good but arbitrage does not work like this in real life.
We have to take into account the spread between the bid and ask side.


### Version 2.1
For the second version, we downlaod the orderbook data using Binance websockts.
Then we make a transaction only when it is profitable using the spread between bid and ask.
Since we only have 1 price for ask and bid, we also make the approximation that there is an unlimited quantity.

When we put a fee, there is no transaction that makes profitable trad over all the data acquired.

If we lower the fee to 0, we have the following result for data acquired during 3 minutes:
<p align='center'>
<img src='https://user-images.githubusercontent.com/96018383/206629149-23a62741-5106-4b6b-b25b-b42c813df2d4.png'>
</p>

This results are still not representative of reality for 2 main reasons : 1) 0% fee might not be realistic and 2) we havn't look for the quantity for each bid and ask.

### Version 2.2
Now, if we take into account the bid and ask quantity, we have much less performance.
We only generate 0.076% over the period (instead of 90% for the V2.1):

<p align='center'>
<img src='https://user-images.githubusercontent.com/96018383/206634825-9b9f8ea3-0952-4a6c-b866-84e8e30ca55f.png'>
</p>


### Version 3

On the third version, we also get the book data with a depth of 20 for both bids and asks.
Every time we make a trade, we update our data to reflect the change in supply.

With 0 fees we have the following graph : 
<p align='center'>
<img src='https://user-images.githubusercontent.com/96018383/210090953-e18a2178-2eac-48b8-a061-c1f0c453bb36.png'>
</p>

And with 0.1% fee per trades, we have the following one :
<p align='center'>
<img src='https://user-images.githubusercontent.com/96018383/210091053-0d4d0a56-942b-4aa8-ae7f-62b17f48ff4c.png'>
</p>

### Version 4 (Todo)

Merge the data collect and the trade part

### Version 5 (Todo)
Deploy live with real trade
Add taker
