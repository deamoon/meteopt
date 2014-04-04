from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross

class Strategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, smaPeriod, cash=1000000):
        strategy.BacktestingStrategy.__init__(self, feed, cash)
        self.__instrument = instrument
        self.__position = None
        self.__Close = feed[instrument].getCloseDataSeries()        
        self.__sma = ma.SMA(self.__Close, smaPeriod)

    def getSMA(self):
        return self.__sma

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        self.__position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def onBars(self, bars):
        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if cross.cross_above(self.__Close, self.__sma) > 0:
                # Enter a buy market order for 1 share. The order is good till canceled.
                print "BUY\n"
                self.__position = self.enterLong(self.__instrument, 1, True)
        # Check if we have to exit the position.
        elif cross.cross_below(self.__Close, self.__sma) > 0:
            print "SELL\n"
            self.__position.exitMarket()