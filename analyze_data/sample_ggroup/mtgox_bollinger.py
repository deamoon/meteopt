#! /usr/bin/python2
# http://gbeced.github.io/pyalgotrade/docs/v0.14/html/mtgox_tutorial.html
# http://gbeced.github.io/pyalgotrade/docs/v0.14/html/sample_bbands.html

# Example resample
# feed = mtgoxfeed.CSVTradeFeed()
# feed.addBarsFromCSV("trades-mtgox-usd-2013-03.csv.bak")
# resample.resample_to_csv(feed, 60*15, "resampled.csv")

import time, math, os, sys, datetime
from dateutil.relativedelta import relativedelta

sys.path.append('/home/richi/Downloads/PyAlgoTrade-0.14')

import pyalgotrade
from pyalgotrade import strategy
from pyalgotrade import plotter
from pyalgotrade.mtgox import tools
from pyalgotrade.mtgox import barfeed
from pyalgotrade.technical import bollinger
from pyalgotrade.tools.resample import resample_to_csv
from pyalgotrade.barfeed.csvfeed import GenericBarFeed

class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, bBandsPeriod):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument
        self.__bbands = bollinger.BollingerBands(feed[instrument].getCloseDataSeries(), bBandsPeriod, 2)

    def getBollingerBands(self):
        return self.__bbands

    def onBars(self, bars):
        lower = self.__bbands.getLowerBand()[-1]
        upper = self.__bbands.getUpperBand()[-1]
        if lower == None:
            return

        shares = self.getBroker().getShares(self.__instrument)
        bar = bars[self.__instrument]
        if shares == 0 and bar.getClose() < lower:
            sharesToBuy = int(self.getBroker().getCash(False) / bar.getClose())
            self.order(self.__instrument, sharesToBuy) 
        elif shares > 0 and bar.getClose() > upper:
            self.order(self.__instrument, -1*shares) 

def main(plot):
    bBandsPeriod = 60 * 24 * 2

    # download and load the historic trade data from mtgox
    currency = 'USD'
    instrument = 'BTC'
    startdate = datetime.date(2013, 1, 1)
    enddate = datetime.date.today() - relativedelta(days=1)
    barFrequency = pyalgotrade.barfeed.Frequency.MINUTE

    print '(down-)loading bars'
    feed = GenericBarFeed(barFrequency)
    month = startdate
    while month <= enddate:
        fnamOrig = 'trades-mtgox-%s-%d-%d.csv' % (currency, month.year, month.month)
        if barFrequency == pyalgotrade.barfeed.Frequency.MINUTE:
            fnamResa = 'resamp1m-mtgox-%s-%d-%d.csv' % (currency, month.year, month.month)
        else:
            fnamResa = 'resamp1h-mtgox-%s-%d-%d.csv' % (currency, month.year, month.month)
        if not os.path.exists(fnamOrig):
            print 'downloading ', fnamOrig
            tools.download_trades_by_month(currency, month.year, month.month, fnamOrig)
        if not os.path.exists(fnamResa):
            print 'resampling ', fnamResa
            feedLocal = barfeed.CSVTradeFeed()
            feedLocal.addBarsFromCSV(fnamOrig)
            resample_to_csv(feedLocal, barFrequency, fnamResa)

        print 'loading ', fnamResa
        feed.addBarsFromCSV(instrument, fnamResa)
        month += relativedelta(months=1)

    print 'set up strategy and plot'
    myStrategy = MyStrategy(feed, instrument, bBandsPeriod)

    if plot:
        plt = plotter.StrategyPlotter(myStrategy, True, True, True)
        plt.getInstrumentSubplot(instrument).addDataSeries("upper", myStrategy.getBollingerBands().getUpperBand())
        plt.getInstrumentSubplot(instrument).addDataSeries("middle", myStrategy.getBollingerBands().getMiddleBand())
        plt.getInstrumentSubplot(instrument).addDataSeries("lower", myStrategy.getBollingerBands().getLowerBand())

    print 'run the strategy'
    myStrategy.run()
    print "Result: %.2f" % myStrategy.getResult()

    if plot:
        plt.plot()

if __name__ == "__main__":
    main(True)
