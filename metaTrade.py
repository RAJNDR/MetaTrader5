import MetaTrader5 as mt5
import time
import pandas as pd
from datetime import datetime
import logging
from CurrencyPair import CurrencyPair as CP

buyingCurrency = 'GBPUSD'
sellingCurrency = 'GBPCHF'
timeFrame = mt5.TIMEFRAME_M10
profitMargin = 30
lossMargin = -10
lotSize = 0.1
cycleTime = 600 #(Trade cycle) in seconds

class tradeClass:
    def __init__(self, buyingCurrency, sellingCurrency, timeFrame, lotSize, cycleTime):
        self.buyPair = CP(buyingCurrency,mt5, pd)
        self.sellPair = CP(sellingCurrency,mt5, pd)
        self.initSelf = True
        self.timeFrame = timeFrame
        self.cycleTime = cycleTime
        self.lotSize = lotSize 
        self.lastCloseBuyingPair = 0.0 
        self.lastCloseSellingPair = 0.0
        self.instProfit = 0.0 # curr
        self.cumulativeProfit = 0.0
        self.openNewPosition = False
        self.closeOpenPositions = False
        self.openPositionBuying = None # curr
        self.openPositionSelling = None # curr
        self.closePositionBuying = None # curr
        self.closePositionSelling = None # curr
        self.lastInstProfitBuying = 0.0
        self.lastInstProfitSelling = 0.0
        self.openPositionBuyingOrderNumber = 0 # curr
        self.openPositionSellingOrderNumber = 0 # curr

        logging.basicConfig(format='%(asctime)s,%(levelname)s,%(message)s', datefmt='%m/%d/%Y,%H:%M:%S')
        self.logger = logging.getLogger('TraderLog')
        self.logger.setLevel(logging.DEBUG)

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
            #get bars of currency pairs
            barBuyingPair = self.buyPair.getBar(timeFrame)
            barSellingPair = self.sellPair.getBar(timeFrame)
            #get closing prices
            closeBuyingPair = barBuyingPair['close'].to_list()[0]
            closeSellingPair = barSellingPair['close'].to_list()[0]
            #run only onetime
            if self.initSelf:
                self.initSelf = False
                self.lastCloseBuyingPair = closeBuyingPair
                self.lastCloseSellingPair = closeSellingPair

            #calculate PIP
            pipBuyingPair = closeBuyingPair - self.lastCloseBuyingPair
            pipSellingPair = closeSellingPair - self.lastCloseSellingPair
            #inst Profit buying pair
            instProfitBuyingPair = self.buyPair.getProfitOnOpenPosition()
            #get inst profit selling pair
            instProfitSellingPair = self.sellPair.getProfitOnOpenPosition()
            #instProfit calc
            self.instProfit = instProfitSellingPair + instProfitBuyingPair
            self.lastInstProfitBuying = instProfitBuyingPair
            self.lastInstProfitSelling = instProfitSellingPair

            self.logger.info("Pair:{},Order:{},Open:{},Close:{},PipChange:{},ProfitInst:{},ProfitCombined:{},ProfitCumm:{}".format(self.buyPair.getSymbol(), self.openPositionBuyingOrderNumber,barBuyingPair['open'].to_list()[0],barBuyingPair['close'].to_list()[0],pipBuyingPair,instProfitBuyingPair,self.instProfit,self.cumulativeProfit))
            self.logger.info("Pair:{},Order:{},Open:{},Close:{},PipChange:{},ProfitInst:{},ProfitCombined:{},ProfitCumm:{}".format(self.sellPair.getSymbol(), self.openPositionSellingOrderNumber,barSellingPair['open'].to_list()[0],barSellingPair['close'].to_list()[0],pipSellingPair,instProfitSellingPair,self.instProfit,self.cumulativeProfit))

            #set bool to open Position
            if self.openPositionBuying is None and self.openPositionSelling is None:
                if (self.instProfit >= 0.0):
                    self.openNewPosition = True

            #Open position
            if self.openNewPosition:
                #Try to open position
                self.openPositionBuyingOrderNumber = 0
                self.openPositionSellingOrderNumber = 0
                self.openNewPosition = False
                self.openPositionBuying = self.buyPair.positionOpen(self.lotSize,mt5.ORDER_TYPE_BUY)
                self.openPositionSelling = self.sellPair.positionOpen(self.lotSize,mt5.ORDER_TYPE_SELL)

                if self.openPositionBuying is None or self.openPositionSelling is None:
                    self.logger.error('Transaction not successfull! wait till next.')
                    self.openPositionBuying = None
                    self.openPositionSelling = None
                    continue

                if (self.openPositionBuying.retcode != mt5.TRADE_RETCODE_DONE) or (self.openPositionSelling.retcode != mt5.TRADE_RETCODE_DONE):
                    self.logger.error("positionBuying exit with Ret code {} and comment {}".format(self.openPositionBuying.retcode,self.openPositionBuying.comment))
                    self.logger.error("openPositionSelling exit with Ret code {} and comment {}".format(self.openPositionSelling.retcode,self.openPositionSelling.comment))
                    self.openPositionBuying = None
                    self.openPositionSelling = None
                    continue
                self.openPositionBuyingOrderNumber = self.openPositionBuying.order
                self.openPositionSellingOrderNumber = self.openPositionSelling.order
                self.logger.warning("POSITION OPEN!")

            #set bool to close position if profit goes out of margin
            if (self.instProfit > profitMargin) or (self.instProfit < lossMargin):
                self.closeOpenPositions = True

            #Close position
            if self.closeOpenPositions:
                self.closeOpenPositions = False
                if (self.openPositionBuying is None) or (self.openPositionSelling is None):
                    self.logger.error('No position Available to close')
                    continue

                self.closePositionBuying = self.buyPair.positionClose(self.lotSize,mt5.ORDER_TYPE_SELL,self.openPositionBuying.order)
                self.closePositionSelling = self.sellPair.positionClose(self.lotSize,mt5.ORDER_TYPE_BUY,self.openPositionSelling.order)

                if self.closePositionBuying is None or self.closePositionSelling is None:
                    logger.error('Position Closing not successfull! wait till next.')
                    continue

                if (self.closePositionBuying.retcode != mt5.TRADE_RETCODE_DONE) or (self.closePositionSelling.retcode != mt5.TRADE_RETCODE_DONE):
                    self.logger.error("closePositionBuying exit with Ret code {} and comment {}".format(self.closePositionBuying.retcode,self.closePositionBuying.comment))
                    self.logger.error("closePositionSelling exit with Ret code {} and comment {}".format(self.closePositionSelling.retcode,self.closePositionSelling.comment))
                    self.openNewPosition = True
                    continue

                self.cumulativeProfit += self.lastInstProfitBuying + self.lastInstProfitSelling

                self.openPositionBuying = None
                self.openPositionSelling = None
                self.closePositionBuying = None
                self.closePositionSelling = None
                self.logger.warning("POSITION CLOSE! at CummulativeProfit: {}".format(self.cumulativeProfit))
            #set variable for previous cycle
            self.lastCloseBuyingPair = closeBuyingPair
            self.lastCloseSellingPair = closeSellingPair

if __name__ == '__main__':
    trade = tradeClass(buyingCurrency,sellingCurrency,timeFrame,lotSize, cycleTime)
    trade.runTrade()



