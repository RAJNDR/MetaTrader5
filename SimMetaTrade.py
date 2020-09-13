import MetaTrader5 as mt5
import time
import pandas as pd
from datetime import datetime
from datetime import timedelta
import logging
#from CurrencyPair import CurrencyPair as CP
from SimCurrencyPair import SimCurrencyPair as CP
import ExpertAdvisor as EA

buyingCurrency = 'GBPUSD'
sellingCurrency = 'GBPCHF'
timeFrame = mt5.TIMEFRAME_M1
profitMargin = 5
lossMargin = -100
spreadMargin = -50
lotSize = 0.1
cycleTime = 60 #(Trade cycle) in seconds
startDateTime = '2020-07-01 00:00:00+00:00'
startDateTime = datetime.fromisoformat(startDateTime)
deltaTime = timedelta(minutes=1)

class SimMetaTradeClass:
    def __init__(self, buyingCurrency, sellingCurrency, timeFrame, lotSize, cycleTime):
        logging.basicConfig(format='%(asctime)s,%(levelname)s,%(message)s', datefmt='%m/%d/%Y,%H:%M:%S')
        self.timeFrame = timeFrame
        self.logger = logging.getLogger('TraderLog')
        self.logger.setLevel(logging.DEBUG)
        self.advisorsList = list()

        if not mt5.initialize():
            logger.error("initialize() failed, error code =" + mt5.last_error()[2])
            mt5.shutdown()
            raise Exception(errorMsg)

        # request connection status and parameters
        print(mt5.terminal_info())
        # get data on MetaTrader 5 version
        print(mt5.version())

    def __del__(self):
        logging.info('close MetaTrader5')
        mt5.shutdown()

    def runTrade(self):
        while True:
            for advisor in self.advisorsList:
                advisor.runAdvisor()
                for pair in advisor.getSellPair():
                    pair.increaseUnitTime()
                for pair in advisor.getBuyPair():
                    pair.increaseUnitTime() 

    def parseConfigAddPairs(self):
        import configparser
        config = configparser.ConfigParser()
        config.read('config.ini')
        for section in config.sections():
            buyingPairsSymbols = config.get(section,'buyingPair')
            buyingPairsSymbols = buyingPairsSymbols.split(',')
            sellingPairsSymbols = config.get(section,'sellingPair')
            sellingPairsSymbols = sellingPairsSymbols.split(',')
            buyingPairs = list()
            sellingPairs = list()
            for pair in buyingPairsSymbols:
                buyingPairs.append(CP(pair,mt5,pd,self.logger,startDateTime,deltaTime,int(config.get(section,'magicNumber'))))
            for pair in sellingPairsSymbols:
                sellingPairs.append(CP(pair,mt5,pd,self.logger,startDateTime,deltaTime,int(config.get(section,'magicNumber'))))
            argDict = {
            'buyingPair':buyingPairs,
            'sellingPair':sellingPairs,
            'timeFrame':timeFrame,
            'lotSize':float(config.get(section,'lotsize')),
            'lossMargin':float(config.get(section,'loss')),
            'spreadMargin':float(config.get(section,'spread')),
            'profitMargin':float(config.get(section,'profit'))
            }
            self.advisorsList.append(EA.HedgedPairAdvisor(argDict,self.logger,mt5))
            self.logger.warning('Added ExperAdvisor! Magic:{} buying:{} selling:{}'.format(config.get(section,'magicNumber'),config.get(section,'buyingPair'),config.get(section,'sellingPair')))

if __name__ == '__main__':
    trade = SimMetaTradeClass(buyingCurrency,sellingCurrency,timeFrame,lotSize, cycleTime)
    trade.parseConfigAddPairs()
    trade.runTrade()



