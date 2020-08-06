import MetaTrader5 as mt5
import time
import pandas as pd
from datetime import datetime, timedelta
import logging
from CurrencyPair import CurrencyPair as CP
import ExpertAdvisor as EA
import SimCurrencyPair as SCP
import pytz

buyingCurrency = 'GBPUSD'
sellingCurrency = 'GBPCHF'
timeFrame = mt5.TIMEFRAME_M2
profitMargin = 30
lossMargin = -10
spreadMargin = -5
lotSize = 0.1
cycleTime = 60 #(Trade cycle) in seconds
timezone = pytz.timezone("Etc/UTC")
startDateTime = datetime(2019,1,1,tzinfo=timezone)
dTime = timedelta(minutes=+60)

class tradeClass:
    def __init__(self, buyingCurrency, sellingCurrency, timeFrame, lotSize, cycleTime):
        logging.basicConfig(format='%(asctime)s,%(levelname)s,%(message)s', datefmt='%m/%d/%Y,%H:%M:%S')
        self.logger = logging.getLogger('TraderLog')
        self.logger.setLevel(logging.DEBUG)
        self.buyPair = SCP.SimCurrencyPair(buyingCurrency,mt5, pd,self.logger,startDateTime,dTime)
        self.sellPair = SCP.SimCurrencyPair(sellingCurrency,mt5, pd,self.logger,startDateTime,dTime)
        self.argDict = {
            'buyingPair':self.buyPair,
            'sellingPair':self.sellPair,
            'timeFrame':timeFrame,
            'lotSize':lotSize,
            'lossMargin':lossMargin,
            'spreadMargin':spreadMargin,
            'profitMargin':profitMargin
        }
        self.expertAdvisor = EA.HedgedPairAdvisor(self.argDict,self.logger,mt5)

        if not mt5.initialize():
            logger.error("initialize() failed, error code =" + mt5.last_error()[2])
            mt5.shutdown()
            raise Exception(errorMsg)
        
        self.buyPair.init()
        self.sellPair.init()
        # request connection status and parameters
        print(mt5.terminal_info())
        # get data on MetaTrader 5 version
        print(mt5.version())

    def __del__(self):
        logging.info('close MetaTrader5')
        mt5.shutdown()

    def runTrade(self):
        while True:
            self.expertAdvisor.runAdvisor()
            self.buyPair.increaseUnitTime()
            self.sellPair.increaseUnitTime()

if __name__ == '__main__':
    trade = tradeClass(buyingCurrency,sellingCurrency,timeFrame,lotSize, cycleTime)
    trade.runTrade()



