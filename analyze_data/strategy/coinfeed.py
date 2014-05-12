from pyalgotrade import dataseries
from pyalgotrade import strategy
from pyalgotrade import barfeed
from pyalgotrade.barfeed import csvfeed
from pyalgotrade import bar
import datetime

class RowParser(csvfeed.RowParser):
    def __init__(self, startDate, endDate):
        self.__startDate = startDate
        self.__endDate = endDate

    def getFieldNames(self):
        # It is expected for the first row to have the field names.
        return None

    def getDelimiter(self):
        return ","

    def parseBar(self, csvRowDict):
        dateTime = datetime.datetime.strptime(csvRowDict["datetime"], "%Y-%m-%d %H:%M:%S")
        if dateTime < self.__startDate or dateTime > self.__endDate:
            return None

        price = float(csvRowDict["price"])
        volume = float(csvRowDict["volume"])
        
        return bar.BasicBar(dateTime, price, price, price, price, volume, None, barfeed.Frequency.TRADE)

class Feed(csvfeed.BarFeed):
    def __init__(self):
        csvfeed.BarFeed.__init__(self, barfeed.Frequency.TRADE, maxLen=dataseries.DEFAULT_MAX_LEN)
        self.__startDate = datetime.datetime.min
        self.__endDate = datetime.datetime.max

    def barsHaveAdjClose(self):
        return False

    def addBarsFromCSV(self, instrument, path):        
        rowParser = RowParser(self.__startDate, self.__endDate)
        csvfeed.BarFeed.addBarsFromCSV(self, instrument, path, rowParser)
    
    def setDateRange(self, startDate, endDate):
        self.__startDate = startDate
        self.__endDate = endDate


if __name__ == '__main__':
    class Strategy(strategy.BacktestingStrategy):
        def onBars(self, bars):
            print bars.getDateTime(), bars["TEST"].getClose(), bars["TEST"].getVolume()

    feed = Feed()
    feed.addBarsFromCSV("TEST", "ticker.csv")
    strat = Strategy(feed)
    strat.run()