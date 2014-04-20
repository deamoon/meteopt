from pyalgotrade import plotter
import smacross_strategy
import coinfeed

# Import data
feed = coinfeed.Feed()
feed.addBarsFromCSV("btc", "data/ticker.csv")

# Evaluate the strategy with the feed's bars.
myStrategy = smacross_strategy.Strategy(feed, "btc", 30)

# Attach the plotter to the strategy.
plt = plotter.StrategyPlotter(myStrategy)
# Include the SMA in the instrument's subplot to get it displayed along with the closing prices.
plt.getInstrumentSubplot("btc").addDataSeries("SMA", myStrategy.getSMA())

# Run the strategy.
myStrategy.run()
myStrategy.info("Final portfolio value: $%.2f" % myStrategy.getResult())

# Plot the strategy.
plt.plot()