import coinfeed
from pyalgotrade.tools.resample import resample_to_csv

def resampleCsv(minutes):
	"""Change interval of data trades with recalc prices"""
	feed = coinfeed.Feed()
	feed.addBarsFromCSV("btc", "data/ticker.csv")
	resample_to_csv(feed, 60 * minutes, "resampled.csv")

if __name__ == '__main__':
	resampleCsv(15)