# MeteOpt
#
# Copyright 2014 Dmitry Ivanovsky

import os
import urllib
from google.appengine.api import users
from google.appengine.ext import ndb
import jinja2
import webapp2
import sys
import logging

import libs

import datetime
from google.appengine.ext import db

def onBotError(msg, tracebackText):
        tstr = time.strftime("%Y/%m/%d %H:%M:%S")
        logging.debug("%s - %s" % (tstr, msg))
        # open("hello-world-bot-error.log", "a").write(
        #     "%s - %s\n%s\n%s\n" % (tstr, msg, tracebackText, "-"*80))

def runBot(bot, buy_floor, sell_ceiling, live_trades = False):        
    # Load the keys and create an API object from the first one.
    key_file = "account.txt"
    handler = btceapi.KeyHandler(key_file)
    key = handler.getKeys()[0]
    logging.debug("Trading with key %s" % key)
    sys.stdout.flush()
    api = btceapi.TradeAPI(key, handler)
            
    # Create a trader that handles LTC/USD trades in the given range.
    trader = RangeTrader(api, "btc_usd", buy_floor, sell_ceiling, live_trades)

    # Create a bot and add the trader to it.
    bot = btcebot.Bot()
    bot.addTrader(trader)
    
    # Add an error handler so we can print info about any failures
    bot.addErrorHandler(onBotError)    

    # The bot will provide the traders with updated information every
    # 15 seconds.
    bot.setCollectionInterval(15)
    bot.start()
    logging.debug("Running; press Ctrl-C to stop")
    sys.stdout.flush()
    
    try:
        while 1:
            # you can do anything else you prefer in this loop while 
            # the bot is running in the background
            time.sleep(3600)
            sys.stdout.flush()
            
    except KeyboardInterrupt:        
        logging.debug("Stopping...")
    finally:         
        bot.stop() 

def tickerToString(ticker):
    attrs = ('high', 'low', 'avg', 'vol', 'vol_cur', 'last',
         'buy', 'sell', 'updated', 'server_time')
    res = ""
    for a in attrs:
        res += "\t%s %s" % (a, getattr(ticker, a))
    return res

class Ticker(db.Model):
    high = db.FloatProperty()
    low = db.FloatProperty()
    avg = db.FloatProperty()
    vol = db.FloatProperty()
    vol_cur = db.FloatProperty()
    last = db.FloatProperty()
    buy = db.FloatProperty()
    sell = db.FloatProperty()
    updated = db.DateTimeProperty()
    server_time = db.DateTimeProperty()

def addTicker(ticker):
    t = Ticker(high=float(ticker.high),
               low=float(ticker.low),
               avg=float(ticker.avg),
               vol=float(ticker.vol),
               vol_cur=float(ticker.vol_cur),
               last=float(ticker.last),
               buy=float(ticker.buy),
               sell=float(ticker.sell),
               updated=ticker.updated,
               server_time=ticker.server_time)    
    t.put()


class Runner(webapp2.RequestHandler):
    def get(self):
        t = libs.btceapi.getTicker("btc_usd")
        self.response.write(tickerToString(t))
        addTicker(t)        
        
        return
        command = self.request.get('command', 0)
        if command == "start":
            if self.running:
                self.response.write('It is running yet')
            else:
                self.start()        
                self.response.write('Bot have run yet')
        elif command == "stop":
            if self.running:
                self.stop()
                self.response.write('Bot was stopped')
            else:                
                self.response.write('Bot have stopped yet')                    
        elif command == "log":
            with open("samples/log.txt", "r") as f:
                self.response.write(f.readlines())
            with open("samples/hello-world-bot-error.log", "r") as f:
                self.response.write(f.readlines())    
        elif command == "clear":
            with open("samples/log.txt", "w") as f:
                pass
            with open("samples/hello-world-bot-error.log", "w") as f:
                pass

    def start(self):
        self.running = True
        self.thread = threading.Thread(target = runBot, args=(self,560, 561))
        self.thread.start()
    
    def stop(self):
        self.running = False
        self.thread.join()
       
application = webapp2.WSGIApplication([
    ('/add_ticker', Runner),
], debug=True)
