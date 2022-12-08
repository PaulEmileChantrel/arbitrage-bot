# Arbitrage bot

In this project, we create an arbitrage bot.

For the first version, we download OHLCV minutes data for BTC/USDT, ETH/USDT and ETH/BTC on Binance.
Then, we go through the data and only make a transaction when we can buy BTC/USDT, then buy ETH/USDT, and then sell ETH/UDST and be profitable with fees or when we can buy ETH/USDT, sell ETH/BTC and sell BTC/USDT and be profitable with fees.

We are able to go from $1,000,000 to $3,208,288 with the data going from Feb. 9, 2018 to Dec. 7 2022.

<p align='center'>
<img src='https://user-images.githubusercontent.com/96018383/206340771-15e335f6-f8f3-405d-aa1e-e1b9a3918592.png'>

</p>

This algorythm is good but arbitrage does not work like this in real life.
We have to take into account the spread between the bid and ask side.


