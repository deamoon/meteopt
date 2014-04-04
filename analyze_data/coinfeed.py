from pyalgotrade import dataseries
from pyalgotrade import strategy
from pyalgotrade import barfeed
from pyalgotrade.barfeed import csvfeed
from pyalgotrade import bar
import datetime

class RowParser(csvfeed.RowParser):
    def getFieldNames(self):
        # It is expected for the first row to have the field names.
        return None

    def getDelimiter(self):
        return ","

    def parseBar(self, csvRowDict):
        dateTime = datetime.datetime.strptime(csvRowDict["datetime"], "%Y-%m-%d %H:%M:%S")
        price = float(csvRowDict["price"])
        volume = float(csvRowDict["volume"])
        return bar.BasicBar(dateTime, price, price, price, price, volume, None, barfeed.Frequency.TRADE)

class Feed(csvfeed.BarFeed):
    def __init__(self):
        csvfeed.BarFeed.__init__(self, barfeed.Frequency.TRADE, maxLen=dataseries.DEFAULT_MAX_LEN)

    def barsHaveAdjClose(self):
        return False

    def addBarsFromCSV(self, instrument, path):
        rowParser = RowParser()
        csvfeed.BarFeed.addBarsFromCSV(self, instrument, path, rowParser)


if __name__ == '__main__':
    class Strategy(strategy.BacktestingStrategy):
        def onBars(self, bars):
            print bars.getDateTime(), bars["TEST"].getClose(), bars["TEST"].getVolume()

    feed = Feed()
    feed.addBarsFromCSV("TEST", "ticker.csv")
    strat = Strategy(feed)
    strat.run()