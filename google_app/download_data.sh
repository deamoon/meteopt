export PATH=$PATH:/home/deamoon/Downloads/google_appengine
rm ticker.csv
rm ticker_yahoo.csv
appcfg.py download_data --config_file=bulkloader.yaml --filename=ticker.csv --kind=Ticker --url=http://pytradebot2.appspot.com/_ah/remote_api
rm bulkloader-*
# python convertData.py
# rm ticker.csv