import MetaTrader5 as mt5
import time
import pandas as pd
from datetime import datetime
import logging

buyingCurrency = 'GBPUSD'
sellingCurrency = 'GBPCHF'
timeFrame = mt5.TIMEFRAME_M10
profitMargin = 30
lossMargin = -10
lotSize = 0.1
cycleTime = 600 #(Trade cycle) in seconds 

class tradeClass:
    def __init__(self,buyingCurrency,sellingCurrency,timeFrame,lotSize, cycleTime):
        self.initSelf = True
        self.buyingCurrency = buyingCurrency
        self.sellingCurrency = sellingCurrency
        self.timeFrame = timeFrame
        self.cycleTime = cycleTime
        self.lotSize = lotSize
        self.lastCloseBuyingPair = 0.0
        self.lastCloseSellingPair = 0.0
        self.instProfit = 0.0
        self.cumulativeProfit = 0.0
        self.openNewPosition = False
        self.closeOpenPositions = False
        self.openPositionBuying = None
        self.openPositionSelling = None
        self.closePositionBuying = None
        self.closePositionSelling = None
        self.lastInstProfitBuying = 0.0
        self.lastInstProfitSelling = 0.0
        self.openPositionBuyingOrderNumber = 0
        self.openPositionSellingOrderNumber = 0

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

    def test(self):
        for i in range(100):
            #Get Bars Per unit Time
            buyingCurrencyBar = mt5.copy_rates_from_pos(self.buyingCurrency, timeFrame, 0, 1)
            sellingCurrencyBar = mt5.copy_rates_from_pos(self.sellingCurrency, timeFrame, 0, 1)
            buyingCurrencyBar_frame = pd.DataFrame(buyingCurrencyBar)
            sellingCurrencyBar_frame = pd.DataFrame(sellingCurrencyBar)
            buyingCurrencyBar_frame['time']=pd.to_datetime(buyingCurrencyBar_frame['time'], unit='s')
            sellingCurrencyBar_frame['time']=pd.to_datetime(sellingCurrencyBar_frame['time'], unit='s')

            print(buyingCurrencyBar_frame)
            time.sleep(1)

    def positionOpen(self, currency, amount, orderType):
        #point = mt5.symbol_info(currency).point
        if orderType == mt5.ORDER_TYPE_BUY:
            price = mt5.symbol_info_tick(currency).ask
        elif orderType == mt5.ORDER_TYPE_SELL:
            price = mt5.symbol_info_tick(currency).bid

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": currency,
            "volume": amount,
            "type": orderType,
            "price": price,
            "sl": 0.0,
            "tp": 0.0,
            "deviation": 1,
            "magic": 234000,
            "comment": "python script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
        result = mt5.order_send(request)
        return result

    def positionClose(self, currency,amount, orderType, orderNumber):
        if orderType == mt5.ORDER_TYPE_BUY:
            price = mt5.symbol_info_tick(currency).ask
        elif orderType == mt5.ORDER_TYPE_SELL:
            price = mt5.symbol_info_tick(currency).bid

        request={
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": currency,
            "volume": amount,
            "type": orderType,
            "position": orderNumber,
            "price": price,
            "deviation": 1,
            "magic": 234000,
            "comment": "python script close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
        result = mt5.order_send(request)
        return result

    def getSellProfit(self, currency, amount, priceAtPositionOpen, closingPrice):
        #todo: implement this
        return mt5.order_calc_profit(mt5.ORDER_TYPE_SELL,currency,amount,priceAtPositionOpen,closingPrice)
        #return

    def getBuyProfit(self, currency, amount, priceAtPositionOpen, closingPrice):
        #todo: implement this
        return mt5.order_calc_profit(mt5.ORDER_TYPE_BUY,currency,amount,priceAtPositionOpen,closingPrice)
        #return

    def getBar(self,currency, timeFrame):
        currencyBar = mt5.copy_rates_from_pos(currency, timeFrame, 0, 1)
        currencyBar_frame = pd.DataFrame(currencyBar)
        currencyBar_frame['time']=pd.to_datetime(currencyBar_frame['time'], unit='s')
        return currencyBar_frame

    def runTrade(self):
        while True:
            time.sleep(cycleTime)
            #get bars of currency pairs
            barBuyingPair = self.getBar(self.buyingCurrency,timeFrame)
            barSellingPair = self.getBar(self.sellingCurrency,timeFrame)
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
            openPositionBuyingPair = mt5.positions_get(symbol=self.buyingCurrency)
            if len(openPositionBuyingPair) == 0:
                instProfitBuyingPair = 0
            else:
                instProfitBuyingPair = openPositionBuyingPair[0].profit

            #get inst profit selling pair
            openPositionSellingPair = mt5.positions_get(symbol=self.sellingCurrency)
            if len(openPositionSellingPair) == 0:
                instProfitSellingPair = 0
            else:
                instProfitSellingPair = openPositionSellingPair[0].profit

            #instProfit calc
            self.instProfit = instProfitSellingPair + instProfitBuyingPair
            self.lastInstProfitBuying = instProfitBuyingPair
            self.lastInstProfitSelling = instProfitSellingPair

            self.logger.info("Pair:{},Order:{},Open:{},Close:{},PipChange:{},ProfitInst:{},ProfitCombined:{},ProfitCumm:{}".format(self.buyingCurrency, self.openPositionBuyingOrderNumber,barBuyingPair['open'].to_list()[0],barBuyingPair['close'].to_list()[0],pipBuyingPair,instProfitBuyingPair,self.instProfit,self.cumulativeProfit))
            self.logger.info("Pair:{},Order:{},Open:{},Close:{},PipChange:{},ProfitInst:{},ProfitCombined:{},ProfitCumm:{}".format(self.sellingCurrency, self.openPositionSellingOrderNumber,barSellingPair['open'].to_list()[0],barSellingPair['close'].to_list()[0],pipSellingPair,instProfitSellingPair,self.instProfit,self.cumulativeProfit))

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
                self.openPositionBuying = self.positionOpen(self.buyingCurrency,lotSize,mt5.ORDER_TYPE_BUY)
                self.openPositionSelling = self.positionOpen(self.sellingCurrency,lotSize,mt5.ORDER_TYPE_SELL)

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

                self.closePositionBuying = self.positionClose(buyingCurrency,lotSize,mt5.ORDER_TYPE_SELL,self.openPositionBuying.order)
                self.closePositionSelling = self.positionClose(sellingCurrency,lotSize,mt5.ORDER_TYPE_BUY,self.openPositionSelling.order)

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



