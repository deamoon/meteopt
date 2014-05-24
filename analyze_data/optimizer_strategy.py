# MeteOpt
#
# Copyright 2014 Dmitry Ivanovsky

from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
from pyalgotrade.broker import backtesting
from pyalgotrade import plotter
from pyalgotrade import barfeed
from strategy import coinfeed
import datetime
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.technical import bollinger
from pyalgotrade.technical import vwap
from pyalgotrade.barfeed import yahoofeed
from genetic_optimizer import genetic
from genetic_optimizer import genetic_old

class UnionStrategy(strategy.BaseStrategy):
    def __init__(self, feed, instrument, parametres, cash=10, comission=0.002):
        broker = backtesting.Broker(cash, feed, backtesting.TradePercentage(comission))
        strategy.BaseStrategy.__init__(self, feed, broker)        
        
        self.numOrder = 0
        self.okOrder = 0
        self.exitOrder = 0
        self.s1 = self.s2 = self.s3 = 1
        self.p1 = self.p2 = self.p3 = 1
        self.windowTrust = parametres[3]

        # SMA
        self.__instrument = instrument
        self.__position = None
        self.__Close = feed[instrument].getCloseDataSeries()                
        self.__sma = ma.SMA(self.__Close, parametres[0])                
        
        # Bbands
        self.__instrument = instrument
        self.__bbands = bollinger.BollingerBands(feed[instrument].getCloseDataSeries(), parametres[1], 2)

        # Vwap
        self.__instrument = instrument
        self.__vwap = vwap.VWAP(feed[instrument], parametres[2])

    def onBars(self, bars):
        lower = self.__bbands.getLowerBand()[-1]
        upper = self.__bbands.getUpperBand()[-1]
        if lower is None:
            return
        vwap = self.__vwap[-1]
        if vwap is None:
            return

        shares = self.getBroker().getShares(self.__instrument)
        bar = bars[self.__instrument]
        price = bars[self.__instrument].getClose()
        
        update = lambda a, b, s: self.windowTrust if a > b else s-1

        self.s1 = update(price, self.__sma[-1], self.s1)
        self.s2 = update(price, upper, self.s2)
        # self.s3 = update(vwap * 0.995, price, self.s3)
        self.s3 = 1         

        if self.__position is None:                        
            self.p1 = update(self.__sma[-1], price, self.p1)
            self.p2 = update(lower, price, self.p2)
            # self.p3 = update(price, vwap * 1.005, self.p3)
            self.p3 = 1            
            if self.p1 >= 1 and self.p2 >= 1 and self.p3 >= 1:
                self.buyPrice = bars.getBar("btc").getClose()                
                quantity = self.getBroker().getCash() / bars.getBar("btc").getClose() * 0.99
                self.__position = self.enterLong(self.__instrument, quantity)                
                self.numOrder += 1
        elif self.s1 >= 1 and self.s2 >= 1 and self.s3 >= 1:
            # if (abs(self.buyPrice - bars.getBar("btc").getClose()) > 0.002 * (bars.getBar("btc").getClose())):
            # if (abs(self.buyPrice - bars.getBar("btc").getClose()) > 10):            
            self.__position.exitMarket()

    def onEnterCanceled(self, position):
        # print "onEnterCanceled"
        self.exitOrder += 1
        self.__position = None

    def onExitOk(self, position):
        self.okOrder += 1        
        self.__position = None

    def onExitCanceled(self, position):    
        print "onExitCanceled"        
        self.__position.exitMarket()  

class GeneticData:
    def __init__(self):
        self.description = ("smaPeriod", "bBandsPeriod", "vwapWindowSize", "windowTrust")
        self.lowerBound = (5, 5, 5, 1)
        self.upperBound = (100, 100, 100, 10)
        self.parseData()

    def parseData(self):
        self.feed = coinfeed.Feed()
        startDate = datetime.datetime.strptime("2014-04-06 11:47:42", "%Y-%m-%d %H:%M:%S")
        endDate   = datetime.datetime.strptime("2014-04-16 11:47:42", "%Y-%m-%d %H:%M:%S")
        # self.feed.setDateRange(startDate, endDate)
        self.feed.addBarsFromCSV("btc", "data/ticker.csv")        
        
        # Manually collect all bars.
        self.bars = []
        self.feed.start()
        for date, bar in self.feed:            
            self.bars.append(bar)
        self.feed.stop()
        self.feed.join()

    def resultFunction(self, parametres):
        assert(len(parametres) == len(self.lowerBound))
        self.feed = coinfeed.Feed()
        startDate = datetime.datetime.strptime("2014-04-06 11:47:42", "%Y-%m-%d %H:%M:%S")
        endDate   = datetime.datetime.strptime("2014-04-16 11:47:42", "%Y-%m-%d %H:%M:%S")
        # self.feed.setDateRange(startDate, endDate) 
        self.feed.addBarsFromCSV("btc", "data/ticker.csv")                
        myStrategy = UnionStrategy(self.feed, "btc", parametres)
        myStrategy.run()
        return myStrategy.getResult()

    def resultFunction2(self, parametres):
        assert(len(parametres) == len(self.lowerBound))            
        
        feedToBuildOnEveryLoop = barfeed.OptimizerBarFeed(self.feed.getFrequency(), 
        self.feed.getRegisteredInstruments(), self.bars)        
        
        myStrategy = UnionStrategy(feedToBuildOnEveryLoop, "btc", parametres)
        myStrategy.run()
        return myStrategy.getResult()    


def resultFunction3(a,b,c,d):
    parametres = [a, b, c, d]
    assert(len(parametres) == 4)
    feed = coinfeed.Feed()
    startDate = datetime.datetime.strptime("2014-04-06 11:47:42", "%Y-%m-%d %H:%M:%S")
    endDate   = datetime.datetime.strptime("2014-04-16 11:47:42", "%Y-%m-%d %H:%M:%S")
    # feed.setDateRange(startDate, endDate)        
    feed.addBarsFromCSV("btc", "data/ticker.csv")                
    myStrategy = UnionStrategy(feed, "btc", parametres)
    myStrategy.run()
    return myStrategy.getResult()

def parameters_generator():
    smaPeriod = range(5, 100)
    bBandsPeriod = range(5, 100)
    vwapWindowSize = range(5, 100)
    return itertools.product(smaPeriod, bBandsPeriod, vwapWindowSize)

def main():
    opt = GeneticOptimizer()
    opt.run(parameters_generator(), resultFunction)

def plot():
    feed = coinfeed.Feed()        
    feed.addBarsFromCSV("btc", "data/ticker.csv")
    myStrategy = UnionStrategy(feed, "btc", [27, 56, 76, 3])
    plt = plotter.StrategyPlotter(myStrategy)    
    myStrategy.run()
    myStrategy.info("Final portfolio value: $%.2f" % myStrategy.getResult())
    print "Number of orders = %d" % myStrategy.numOrder
    print "Number of OK orders = %d" % myStrategy.okOrder
    print "Number of exit orders = %d" % myStrategy.exitOrder    
    plt.plot()
   
def whySoSlow():    
    feed = coinfeed.Feed()
    feed.addBarsFromCSV("btc", "data/ticker.csv")                
        
    gdata = GeneticData()    
    print gdata.resultFunction((30, 5, 10, 1))
    print gdata.resultFunction((30, 5, 10, 2))
    print gdata.resultFunction((30, 5, 10, 3))
    print gdata.resultFunction((30, 5, 10, 4))

def opt():
    d = GeneticData()    
    g = genetic.GeneticOptimizer(10, d, num_of_threads = 1)
    #g = genetic.GeneticOptimizer(3, resultFunction3, 
    #   d.lowerBound, d.upperBound, [True, True, True, True],)
    g.run(6)
    print '\n'.join([str(x) for x in g.population])
    print '\n'.join([str(x) for x in g.results])

if __name__ == '__main__':
    # opt()
    # exit()
    d = GeneticData()
    print d.resultFunction([36, 5, 27, 1])
    print resultFunction3(36, 5, 27, 1)
