from pyalgotrade import strategy
from pyalgotrade import plotter
from pyalgotrade.tools import yahoofinance
from pyalgotrade.technical import vwap
from strategy import coinfeed
from pyalgotrade.broker import backtesting

class MyStrategy(strategy.BaseStrategy):
    def __init__(self, feed, instrument, vwapWindowSize, cash=10, comission=0.002):
        broker = backtesting.Broker(cash, feed, backtesting.TradePercentage(comission))
        strategy.BaseStrategy.__init__(self, feed, broker)

        self.__instrument = instrument
        self.__vwap = vwap.VWAP(feed[instrument], vwapWindowSize)

    def getVWAPDS(self):
        return self.__vwap

    def onBars(self, bars):
        vwap = self.__vwap[-1]
        if vwap is None:
            return

        shares = self.getBroker().getShares(self.__instrument)
        price = bars[self.__instrument].getClose()
        notional = shares * price
        if price < vwap * 0.995 and notional > 0:
            self.marketOrder(self.__instrument, -0.02)
        elif price > vwap * 1.005 and notional < 1000000:
            self.marketOrder(self.__instrument, 0.02)


def main(plot):
    instrument = "btc"
    vwapWindowSize = 20

    # Download the bars.
    # feed = yahoofinance.build_feed([instrument], 2011, 2012, ".")

    feed = coinfeed.Feed()
    # startDate = datetime.datetime.strptime("2014-04-06 11:47:42", "%Y-%m-%d %H:%M:%S")
    # endDate   = datetime.datetime.strptime("2014-04-10 11:47:42", "%Y-%m-%d %H:%M:%S")
    # feed.setDateRange(startDate, endDate)
    feed.addBarsFromCSV(instrument, "data/ticker.csv")

    myStrategy = MyStrategy(feed, instrument, vwapWindowSize)

    if plot:
        # plt = plotter.StrategyPlotter(myStrategy, True, False, True)
        plt = plotter.StrategyPlotter(myStrategy)
        plt.getInstrumentSubplot(instrument).addDataSeries("vwap", myStrategy.getVWAPDS())


    myStrategy.run()
    print "Result: %.2f" % myStrategy.getResult()

    if plot:
        plt.plot()

if __name__ == "__main__":
    main(True)
