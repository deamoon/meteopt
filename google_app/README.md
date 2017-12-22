Instruction
===========

If you want to download new ticker's data from database run download_data.sh, result in ticker_yahoo.csv	

```
export PATH=$PATH:/home/deamoon/Downloads/google_appengine
export PATH=$PATH:/home/deamoon/Downloads/google_appengine/lib

cd /home/deamoon/Documents/bitcoin/google_app/appengine-django-skeleton

./manage.py runserver

appcfg.py --oauth2 update .

http://pytradebot.appspot.com/

http://localhost:8000/_ah/admin

http://localhost:8000

http://localhost:8000/admin

cd /home/deamoon/Documents/bitcoin/google_app

appcfg.py --oauth2 update btcbot/

dev_appserver.py btcbot/

python googleappengine/tools/updateapp.py --app_id=pytradebot --app_path=googleappengine/app

python -c "from pyalgotrade.tools import yahoofinance; print yahoofinance.download_daily_bars('dia', 2009, 'dia-2009.csv')"

python googleappengine/tools/uploadbars.py --instrument=dia --url=http://pytradebot.appspot.com/remote_api dia-2009.csv dia-2010.csv dia-2011.csv

appcfg.py download_data --config_file=bulkloader.yaml --filename=ticker.csv --kind=Ticker --url=http://pytradebot2.appspot.com/_ah/remote_api

appcfg.py create_bulkloader_config --filename=bulkloader.yaml --url=http://pytradebot2.appspot.com/_ah/remote_api
```