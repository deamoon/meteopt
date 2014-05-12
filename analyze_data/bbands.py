from pyalgotrade import strategy
from pyalgotrade import plotter
from pyalgotrade.tools import yahoofinance
from pyalgotrade.technical import bollinger
from strategy import coinfeed
import datetime
from pyalgotrade.broker import backtesting

class MyStrategy(strategy.BaseStrategy):
    def __init__(self, feed, instrument, bBandsPeriod, cash=10, comission=0.002):
        broker = backtesting.Broker(cash, feed, backtesting.TradePercentage(comission))
        strategy.BaseStrategy.__init__(self, feed, broker)
                
        self.__instrument = instrument
        self.__bbands = bollinger.BollingerBands(feed[instrument].getCloseDataSeries(), bBandsPeriod, 2)

    def getBollingerBands(self):
        return self.__bbands

    def onBars(self, bars):
        lower = self.__bbands.getLowerBand()[-1]
        upper = self.__bbands.getUpperBand()[-1]
        if lower is None:
            return

        shares = self.getBroker().getShares(self.__instrument)
        bar = bars[self.__instrument]
        if shares == 0 and bar.getClose() < lower:            
            sharesToBuy = self.getBroker().getCash(False) / bar.getClose() * 0.99
            self.marketOrder(self.__instrument, sharesToBuy)
        elif shares > 0 and bar.getClose() > upper:
            self.marketOrder(self.__instrument, -1*shares)


def bbandsResultPortfolio(bBandsPeriod):    
    feed = coinfeed.Feed()
    feed.addBarsFromCSV("btc", "data/ticker.csv")
    myStrategy = MyStrategy(feed, "btc", bBandsPeriod)
    myStrategy.run()
    return myStrategy.getResult()

def main(plot):
    instrument = "yhoo"
    bBandsPeriod = 10

    # Download the bars.
    # feed = yahoofinance.build_feed([instrument], 2011, 2012, ".")
    feed = coinfeed.Feed()
    startDate = datetime.datetime.strptime("2014-04-06 11:47:42", "%Y-%m-%d %H:%M:%S")
    endDate   = datetime.datetime.strptime("2014-04-10 11:47:42", "%Y-%m-%d %H:%M:%S")
    # feed.setDateRange(startDate, endDate)
    feed.addBarsFromCSV("btc", "data/ticker.csv")

    myStrategy = MyStrategy(feed, "btc", bBandsPeriod)

    if plot:
        plt = plotter.StrategyPlotter(myStrategy, True, True, True)
        plt.getInstrumentSubplot(instrument).addDataSeries("upper", myStrategy.getBollingerBands().getUpperBand())
        # plt.getInstrumentSubplot(instrument).addDataSeries("middle", myStrategy.getBollingerBands().getMiddleBand())
        plt.getInstrumentSubplot(instrument).addDataSeries("lower", myStrategy.getBollingerBands().getLowerBand())

    myStrategy.run()
    print "Result: %.2f" % myStrategy.getResult()

    if plot:
        plt.plot()

if __name__ == "__main__":
    main(True)
