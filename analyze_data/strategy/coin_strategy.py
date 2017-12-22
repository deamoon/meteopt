import pyalgotrade.broker
from pyalgotrade.broker import backtesting
from pyalgotrade import observer
from pyalgotrade import dispatcher
import pyalgotrade.strategy.position
from pyalgotrade import warninghelpers
from pyalgotrade import logger
from pyalgotrade import strategy

class BitcoinStrategy(strategy.BaseStrategy):
    """Base class for backtesting strategies.

    :param barFeed: The bar feed to use to backtest the strategy.
    :type barFeed: :class:`pyalgotrade.barfeed.BaseBarFeed`.
    :param cash: The amount of cash available.
    :type cash: int/float.

    .. note::
        This is a base class and should not be used directly.
    """

    def __init__(self, barFeed, cash=1000000):
        # The broker should subscribe to barFeed events before the strategy.
        # This is to avoid executing orders placed in the current tick.
        broker = backtesting.Broker(cash, barFeed, backtesting.TradePercentage(0.002))
        strategy.BaseStrategy.__init__(self, barFeed, broker)
        self.__useAdjustedValues = False
        self.setUseEventDateTimeInLogs(True)

    def getUseAdjustedValues(self):
        return self.__useAdjustedValues

    def setUseAdjustedValues(self, useAdjusted):
        if not self.getFeed().barsHaveAdjClose():
            raise Exception("The barfeed doesn't support adjusted close values")
        self.getBroker().setUseAdjustedValues(useAdjusted, True)
        self.__useAdjustedValues = useAdjusted