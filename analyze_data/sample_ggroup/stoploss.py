from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade import broker
from pyalgotrade import plotter

"""
Can some paste some example on how to implement stop loss feature?
In the tutorial,  the is an SMA  strategy,  http://gbeced.github.io/pyalgotrade/docs/v0.14/html/tutorial.html 

Can you add one stop loss exit signal? 
for example,  if long trade is opened on this bar, use the current bar Low as stop loss, and current bar high for the short trade. 

And an tutorial for Turtle trading rule would be great (BreakOut Entry,  Trading Stops, and position size ) 
Some links might be helpful 
http://bigpicture.typepad.com/comments/files/turtlerules.pdf  (System detail) 
https://www.quantopian.com/posts/turtle-trading-strategy     And personally I think PyAlogTrade will do better than Zipline on real complicated system. 

--------------------

Hi,
This is not exactly the strategy you're requesting but it should point you in the right direction for implementing take-profit and stop-loss.
I'm not using the position interface (enterLong(...), etc) because right now it is rather limited for this scenarios. This is why I'm creating and placing orders manually.
Let me know if this helps.

--------------------

Thanks, it is very helpful, Now I notice there is more feature than I thought: onOrderUpdated(
put all the order. stuff in onBars would be more convenient.


onBars (presudo code) 

         check the open orders for P&L
         check  pending order get filled or canceled  
         If  condition meat:
                 ceate stop or limit orders (open orders) 
        If  condition meat:
                 Modify stop loss    (trailing or change the stops based on Bars pattern, TA 
        If  condition meat:
                  exit some open orders   ( example, exit after 3 bars after the open is open  ) 



I will spend more time on this if schedule allowed. 
"""

class Strategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, smaPeriod, cash):
        strategy.BacktestingStrategy.__init__(self, feed, cash)
        self.__instrument = instrument
        self.__closeDS = feed[instrument].getCloseDataSeries()
        self.__sma = ma.SMA(self.__closeDS, smaPeriod)
        # Exit and stop loss orders.
        self.__takeProfitOrder = None
        self.__stopLossOrder = None

    def onOrderUpdated(self, order):
        if order.isFilled():
            # Was the take profit order filled ?
            if self.__takeProfitOrder is not None and order.getId() == self.__takeProfitOrder.getId():
                entryPrice = order.getExecutionInfo().getPrice()
                print self.getFeed().getCurrentBars().getDateTime(), "Take profit order filled at", entryPrice
                self.__takeProfitOrder = None
                # Cancel the other exit order to avoid entering a short position.
                self.getBroker().cancelOrder(self.__stopLossOrder)
            # Was the stop loss order filled ?
            elif self.__stopLossOrder is not None and order.getId() == self.__stopLossOrder.getId():
                entryPrice = order.getExecutionInfo().getPrice()
                print self.getFeed().getCurrentBars().getDateTime(), "Stop loss order filled at", entryPrice
                self.__stopLossOrder = None
                # Cancel the other exit order to avoid entering a short position.
                self.getBroker().cancelOrder(self.__takeProfitOrder)
            else: # It is the buy order that got filled.
                entryPrice = order.getExecutionInfo().getPrice()
                shares = order.getExecutionInfo().getQuantity()
                print self.getFeed().getCurrentBars().getDateTime(), "Buy order filled at", entryPrice
                # Submit take-profit and stop-loss orders.
                # In the next version I'll provide a shortcut for this similar to self.order(...) for market orders.
                takeProfitPrice = entryPrice * 1.01
                self.__takeProfitOrder = self.getBroker().createLimitOrder(broker.Order.Action.SELL, self.__instrument, takeProfitPrice, shares)
                self.__takeProfitOrder.setGoodTillCanceled(True)
                self.getBroker().placeOrder(self.__takeProfitOrder)
                stopLossPrice = entryPrice * 0.95
                self.__stopLossOrder = self.getBroker().createStopOrder(broker.Order.Action.SELL, self.__instrument, stopLossPrice, shares)
                self.__stopLossOrder.setGoodTillCanceled(True)
                self.getBroker().placeOrder(self.__stopLossOrder)
                print "Take-profit set at", takeProfitPrice
                print "Stop-loss set at", stopLossPrice

    def getSMA(self):
        return self.__sma

    def onBars(self, bars):
        shares = self.getBroker().getShares(self.__instrument)

        # If a position was not opened, check if we should enter a long position.
        if shares == 0:
            if cross.cross_above(self.__closeDS, self.__sma) > 0:
                # Enter a buy market order for 10 shares. The order is good till canceled.
                self.order(self.__instrument, 10, goodTillCanceled=True)


def main():
    # Load the yahoo feed from the CSV file
    feed = yahoofeed.Feed()
    feed.addBarsFromCSV("orcl", "orcl-2000.csv")

    strat = Strategy(feed, "orcl", 10, 1000)

    # Attach the plotter to the strategy.
    plt = plotter.StrategyPlotter(strat)
    # Include the SMA in the instrument's subplot to get it displayed along with the closing prices.
    plt.getInstrumentSubplot("orcl").addDataSeries("SMA", strat.getSMA())

    # Run the strategy.
    strat.run()
    print "Final portfolio value: $%.2f" % strat.getResult()

    # Plot the strategy.
    plt.plot()

if __name__ == "__main__":
    main()
