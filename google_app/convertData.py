import datetime

inputFile = "ticker.csv"
outputFile = "ticker_yahoo.csv"

with open(inputFile) as f:
    data = f.readlines()

ticker = []
for line in data:
	ticker.append(tuple(line.split(',')))	

ticker = sorted(ticker, key=lambda student: student[0])	

print "Give data for %s - %s\n" % (ticker[0][0], ticker[-2][0])

date = datetime.datetime(2000,1,1,1,1,1)
with open(outputFile, "w") as f:
	f.write("Date,Open,High,Low,Close,Volume,Adj Close\n")
	for tick in ticker[:-1]:
		f.write(str(date.date()) + ",")
		f.write((tick[1].strip() + ",") * 4)
		f.write("1000000,")
		f.write(tick[1])
		date += datetime.timedelta(days=1)