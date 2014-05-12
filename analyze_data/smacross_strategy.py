from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
from pyalgotrade.broker import backtesting
from pyalgotrade import plotter
from strategy import coinfeed
import datetime
from pyalgotrade.stratanalyzer import returns

class SmaStrategy(strategy.BaseStrategy):
    def __init__(self, feed, instrument, smaPeriod, comission=0, cash=10):
        broker = backtesting.Broker(cash, feed, backtesting.TradePercentage(comission))
        strategy.BaseStrategy.__init__(self, feed, broker)
        
        self.__instrument = instrument
        self.__position = None
        self.__Close = feed[instrument].getCloseDataSeries()                
        self.__sma = ma.SMA(self.__Close, smaPeriod)                
        self.numOrder = 0
        self.okOrder = 0
        self.exitOrder = 0
    
    def onBars(self, bars):        
        if self.__position is None:            
            if cross.cross_above(self.__Close, self.__sma) > 0:
                self.buyPrice = bars.getBar("btc").getClose()
                
                quantity = self.getBroker().getCash() / bars.getBar("btc").getClose() * 0.99
                self.__position = self.enterLong(self.__instrument, quantity)
                
                self.numOrder += 1
        elif cross.cross_below(self.__Close, self.__sma) > 0:
            # if (abs(self.buyPrice - bars.getBar("btc").getClose()) > 0.002 * (bars.getBar("btc").getClose())):
            if (abs(self.buyPrice - bars.getBar("btc").getClose()) > 10):            
                self.__position.exitMarket()
    
    def getSMA(self):
        return self.__sma

    def onEnterCanceled(self, position):
        print "onEnterCanceled"
        self.exitOrder += 1
        self.__position = None

    def onExitOk(self, position):
        self.okOrder += 1        
        self.__position = None

    def onExitCanceled(self, position):    
        print "onExitCanceled"        
        self.__position.exitMarket()    

def main():
    feed = coinfeed.Feed()
    startDate = datetime.datetime.strptime("2014-04-06 11:47:42", "%Y-%m-%d %H:%M:%S")
    endDate   = datetime.datetime.strptime("2014-04-10 11:47:42", "%Y-%m-%d %H:%M:%S")
    # feed.setDateRange(startDate, endDate)
    feed.addBarsFromCSV("btc", "data/ticker.csv")

    myStrategy = SmaStrategy(feed, "btc", smaPeriod=30, comission=0.002)

    plt = plotter.StrategyPlotter(myStrategy)
    plt.getInstrumentSubplot("btc").addDataSeries("SMA", myStrategy.getSMA())

    # Attach a returns analyzers to the strategy.
    returnsAnalyzer = returns.Returns()
    myStrategy.attachAnalyzer(returnsAnalyzer)
    # Plot the strategy returns at each bar.
    plt.getOrCreateSubplot("returns").addDataSeries("Net return", returnsAnalyzer.getReturns())
    plt.getOrCreateSubplot("returns").addDataSeries("Cum. return", returnsAnalyzer.getCumulativeReturns())

    myStrategy.run()
    myStrategy.info("Final portfolio value: $%.2f" % myStrategy.getResult())

    print "Number of orders = %d" % myStrategy.numOrder
    print "Number of OK orders = %d" % myStrategy.okOrder
    print "Number of exit orders = %d" % myStrategy.exitOrder
    # print "Money = %f" % (myStrategy.getResult() * (1 - myStrategy.numOrder * 0.002))
    # print myStrategy.getBroker().getCash()
    
    plt.plot()
    
    # # feed = coinfeed.Feed()
    # startDate = datetime.datetime.strptime("2014-04-06 11:47:42", "%Y-%m-%d %H:%M:%S")
    # endDate   = datetime.datetime.strptime("2014-04-10 11:47:42", "%Y-%m-%d %H:%M:%S")
    # # feed.setDateRange(startDate, endDate)
    # # feed.addBarsFromCSV("btc", "data/ticker.csv")

    # myStrategy = SmaStrategy(feed, "btc", smaPeriod=31, comission=0.002)
    # myStrategy.run()
    # myStrategy.info("Final portfolio value: $%.2f" % myStrategy.getResult())
    # print "Number of orders = %d" % myStrategy.numOrder


if __name__ == '__main__':
    main()
