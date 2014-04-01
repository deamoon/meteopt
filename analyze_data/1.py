from pyalgotrade.feed import csvfeed

# feed = csvfeed.Feed("updated", "%Y-%m-%dT%H:%M:%S")
# feed.addValuesFromCSV("ticker.csv")
# for dateTime, value in feed:
#     print dateTime, value

from pyalgotrade import plotter
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.stratanalyzer import returns
import smacross_strategy

# Load the yahoo feed from the CSV file
# feed = yahoofeed.Feed()
# feed.addBarsFromCSV("btc/usd", "ticker.csv")    
feed = csvfeed.Feed("updated", "%Y-%m-%dT%H:%M:%S")
feed.addValuesFromCSV("ticker.csv")
myStrategy = smacross_strategy.Strategy(feed, "btc/usd", 10)
