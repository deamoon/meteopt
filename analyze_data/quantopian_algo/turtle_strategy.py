# https://www.quantopian.com/posts/turtle-trading-strategy

# based off of rules from
# http://bigpicture.typepad.com/comments/files/turtlerules.pdf

# uses ETFs:
# http://etfdb.com/type/commodity/exposure/futures-based/no-leveraged/

# this is just a start, there additional rules that haven't yet been implemented

"""
Turtle trading is a well known trend following strategy that was originally taught by Richard Dennis. 
The basic strategy is to buy futures on a 20-day high (breakout) and sell on a 20-day low, although the full set 
of rules is more intricate. I've modeled the meat of the strategy in Quantopian and used it to trade 
exchange-traded funds (ETFs), in this case just some silver and copper securities.

I used rules from here. From what I have seen, the rules of turtle trading slightly vary from source to source, 
however what's outlined in that PDF seems well-guided and reliable. If you want to adjust the rules you can clone 
this and it should be fairly straightforward from there. I've also added an option in the code if you only want 
to long and not short. To trigger buys and sells, the code calculates the goal amount of shares then works from 
there to determine how many to buy or sell. This method for determining order amount works well for things like 
risk-adjusted portfolio sizes.

This is a pretty fundamental strategy and it seems to work well. There are a few different parameters to play 
with, so clone this and see if you can get some good results or even add to the code in any way.

If you want to experiment with adding different ETFs, you can get ideas from a list of futures like this one. 
From there just Google for whatever ETFs, like "corn etfs", and add the respective symbols to the code.
"""

from collections import deque
import math

atr = ta.ATR(timeperiod=20) # used to calculate 20-day ATR

def initialize(context):
    
    # you can find other tickers at that ETF page above
    context.securities = [
                              sid(37732), # euro
                              sid(40365), # uranium
                              sid(36468), # coffee
                              sid(41309), # ..
                              sid(35691), # ethanol
                         ]
    
    # set to True if only longs are wanted, not shorts
    context.long_only = False
    
    # define dicts for deques to contain past prices
    context.past_highs = dict()
    context.past_lows = dict()

def handle_data(context, data):
    total_price = 0 # to be used later as a sort of benchmark
    
    # for each security in the list
    for security in context.securities:
        total_price += data[security].price
        try:
	        # wait for warmup
            if len(context.past_highs[security]) < 20:
                context.past_highs[security].append(data[security].high)
                context.past_lows[security].append(data[security].low)
                N = atr(data)[security]
                continue
        except:
            # define deques
            context.past_highs[security] = deque([], maxlen=20)
            context.past_lows[security] = deque([], maxlen=20)
            continue
            
        # count how many shares we have in open orders and own
        shares = 0
        for o in get_open_orders(security):
            shares += o.amount
        shares += context.portfolio.positions[security].amount
        
        # determine account size
        current_value = context.portfolio.cash + context.portfolio.positions_value
        if current_value < context.portfolio.starting_cash:
            account_size = -context.portfolio.starting_cash + 2*current_value
        else:
            account_size = current_value
        
        # get 20 day ATR
        N = atr(data)[security]
        
        # compute how many units to buy or sell
        trade_amt = math.floor(account_size*.01/N)
        
        # 20-day high?
        h_20 = True if data[security].price > max(context.past_highs[security]) else False
        
        # 20-day low?
        l_20 = True if data[security].price < min(context.past_lows[security]) else False
        
        goal_shares = shares
        if h_20:
            # long
            goal_shares = trade_amt
        elif l_20:
            # sell or short
            if context.long_only:
                goal_shares = 0
            else:
                goal_shares = -trade_amt
            
        # goal_shares = shares + (amount to buy or sell)
        amt_to_buy = goal_shares - shares
        if amt_to_buy != 0:
            if amt_to_buy > 0:
                log.info("buying %s shares of %s" % (amt_to_buy, security.symbol))
            if amt_to_buy < 0:
                log.info("selling %s shares of %s" % (-amt_to_buy, security.symbol))
            order(security, amt_to_buy)
        
        # keep deques updated
        context.past_highs[security].append(data[security].high)
        context.past_lows[security].append(data[security].low)
        
    # record the total price of all stocks. just a sort of benchmark.
    record(total_price=total_price)