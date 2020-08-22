import MetaTrader5 as mt5
import time
import pandas as pd
from datetime import datetime
import logging
from CurrencyPair import CurrencyPair as CP
import ExpertAdvisor as EA

buyingCurrency = 'GBPUSD'
sellingCurrency = 'GBPCHF'
timeFrame = mt5.TIMEFRAME_M1
profitMargin = 30
lossMargin = -10
spreadMargin = -5
lotSize = 0.1
cycleTime = 60 #(Trade cycle) in seconds

class tradeClass:
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
            time.sleep(cycleTime)
            for advisor in self.advisorsList:
                advisor.runAdvisor()

    def parseConfigAddPairs(self):
        import configparser
        config = configparser.ConfigParser()
        config.read('config.ini')
        for section in config.sections():
            buyingPair = CP(config.get(section,'buyingPair'),mt5,pd,self.logger,int(config.get(section,'magicNumber')))
            middlePair = CP(config.get(section,'middlePair'),mt5,pd,self.logger,int(config.get(section,'magicNumber')))
            sellingPair = CP(config.get(section,'sellingPair'),mt5,pd,self.logger,int(config.get(section,'magicNumber')))
            argDict = {
            'buyingPair':buyingPair,
            'middlePair':middlePair,
            'middlePosition':config.get(section,'middlePosition'),
            'sellingPair':sellingPair,
            'timeFrame':timeFrame,
            'lotSize':lotSize,
            'lossMargin':lossMargin,
            'spreadMargin':spreadMargin,
            'profitMargin':profitMargin
            }
            self.advisorsList.append(EA.HedgedPairAdvisor(argDict,self.logger,mt5))
            self.logger.warning('Added ExperAdvisor! Magic:{} buying:{} {}:{} selling:{}'.format(config.get(section,'magicNumber'),config.get(section,'buyingPair'),config.get(section,'middlePosition'),config.get(section,'middlePair'),config.get(section,'sellingPair')))

if __name__ == '__main__':
    trade = tradeClass(buyingCurrency,sellingCurrency,timeFrame,lotSize, cycleTime)
    trade.parseConfigAddPairs()
    trade.runTrade()



