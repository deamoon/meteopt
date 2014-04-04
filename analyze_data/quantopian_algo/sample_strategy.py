# https://www.quantopian.com/posts/discuss-the-sample-algorithm?c=1

"""
I encourage you to press the "Clone Algorithm" button below. That will copy the code into your "My Algorithms" page. You can then hack, edit, tweak, modify, and change it as you see fit. A couple easy changes you can try:

    Change the sid to a different stock
    Change the vwap to be a different number of days

You can see how the backtest results change with even tiny code updates.

This very basic algorithm comes from our help documentation. In the backtest object below, click the "Source Code" tab to see the code. Read the comments in that code carefully, and you'll get a good idea how to write an algorithm in Quantopian.

Also, you might find the Video Tutorial helpful. It walks you through the same programming concepts. Watch it on YouTube.

P.S. This algorithm was last updated on 11/13/12.
"""

    # For this example, we're going to write a simple momentum script.  When the 
    # stock goes up quickly, we're going to buy; when it goes down quickly, we're
    # going to sell.  Hopefully we'll ride the waves.

    # To run an algorithm in Quantopian, you need two functions: initialize and 
    # handle_data.

def initialize(context):
    # This initialize function sets any data or variables that you'll use in
    # your algorithm.  For instance, you'll want to define the security (or 
    # securities) you want to backtest.  You'll also want to define any 
    # parameters or values you're going to use.

    # In our example, we're looking at Apple.  If you re-type this line 
    # yourself, you'll see the auto-complete that is available for the 
    # security ID.
    context.aapl = sid(24)
    
    # In these two lines, we set the maximum and minimum we want our algorithm 
    # to go long or short our security.  You don't have to set limits like this
    # when you write an algorithm, but it's good practice.
    context.max_notional = 1000000.1
    context.min_notional = -1000000.0

def handle_data(context, data):
    # This handle_data function is where the real work is done.  Our data is
    # minute-level tick data, and each minute is called a frame.  This function
    # runs on each frame of the data.
    
    # We've built a handful of useful data transforms for you to use.  In this 
    # line, we're computing the volume-weighted-average-price of the security 
    # defined above, in the context.aapl variable.  For this example, we're 
    # specifying a three-day average.
    vwap = data[context.aapl].vwap(3)
    # We need a variable for the current price of the security to compare to
    # the average.
    price = data[context.aapl].price
       
    # Another powerful built-in feature of the Quantopian backtester is the
    # portfolio object.  The portfolio ojbect tracks your positions, cash,
    # cost basis of specific holdings, and more.  In this line, we calculate
    # how long or short our position is at this minute.   
    notional = context.portfolio.positions[context.aapl].amount * price
       
    # This is the meat of the algorithm, placed in this if statement.  If the
    # price of the security is .5% less than the 3-day volume weighted average
    # price AND we haven't reached our maximum short, then we call the order
    # command and sell 100 shares.  Similarly, if the stock is .5% higher than
    # the 3-day average AND we haven't reached our maximum long, then we call
    # the order command and buy 100 shares.         
    if price < vwap * 0.995 and notional > context.min_notional:
        order(context.aapl,-100)
    elif price > vwap * 1.005 and notional < context.max_notional:
        order(context.aapl,+100)