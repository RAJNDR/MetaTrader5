from CurrencyPair import CurrencyPair
import datetime
import MetaTrader5 as mt5
from TickData import TickData

class ResultPosition:
    retcode = mt5.TRADE_RETCODE_DONE
    commit = 'Transaction done'
    order = 0
    def __init__(self):
        return

class SimCurrencyPair(CurrencyPair):
    def __init__(self,currencyPair, mt5, pd,logger,startTime,deltaTime,magicNumber):
        super().__init__(currencyPair,mt5,pd,logger,magicNumber)
        self.tickData = TickData(currencyPair,mt5,pd)
        self.time = startTime
        self.deltaTime = deltaTime
        self.bid = 0.0
        self.ask = 0.0
        self.spread = 0.0
        self.profit = 0.0
        self.orderDone = ResultPosition()
        self.positionType = self.mt5.ORDER_TYPE_BUY
        self.lot = 0.0
        self.positionOpened = False
        self.bidOpen = 0.0
        self.askOpen = 0.0
        self.init()

    def init(self):
        time,bid,ask = self.tickData.getTick(self.time)
        self.bid = bid
        self.ask = ask
        self.spread = (self.bid - self.ask) * 10000

    def increaseUnitTime(self):
        self.time += self.deltaTime
        time,bid,ask = self.tickData.getTick(self.time)
        self.bid = bid
        self.ask = ask
        self.spread = (self.bid - self.ask) * 10000
        if self.positionOpened:
            if self.positionType == self.mt5.ORDER_TYPE_BUY:
                self.profit = self.lot * (self.askOpen - self.bid) * 10000
            elif self.positionType == self.mt5.ORDER_TYPE_SELL:
                self.profit = self.lot * (self.bidOpen - self.ask) * 10000

    def getBar(self, timeFrame):
        #todo: fix this
        #d= self.pd.DataFrame.from_dict({'close':[0], 'open':[0]})
        #return d
        currencyBar = self.mt5.copy_rates_from(self.currencyPair, timeFrame, self.time, 1)
        currencyBar_frame = self.pd.DataFrame(currencyBar)
        currencyBar_frame['time']=self.pd.to_datetime(currencyBar_frame['time'], unit='s')
        return currencyBar_frame

    def positionClose(self, amount, orderType, orderNumber):
        self.profit = 0.0
        self.positionOpened = False
        return self.orderDone

    def positionOpen(self, amount, orderType):
        self.positionType = orderType
        self.lot = amount
        self.bidOpen = self.bid
        self.askOpen = self.ask
        self.positionOpened = True
        return self.orderDone

    def getProfitOnOpenPosition(self):
        return self.profit

    def getSpread(self):
        return self.spread

    def closeAllOpenPositions(self):
        return True

class SimCurrencyPairCsv(CurrencyPair):
    def __init__(self,currencyPair, mt5, pd,logger,csv_file):
        super().__init__(currencyPair,mt5,pd,logger)
        self.csv_file = csv_file
        self.bid = 0.0
        self.ask = 0.0
        self.spread = 0.0
        self.profit = 0.0
        self.orderDone = ResultPosition()
        self.positionType = self.mt5.ORDER_TYPE_BUY
        self.lot = 0.0
        self.positionOpened = False
        self.bidOpen = 0.0
        self.askOpen = 0.0
        self.reader = self.pd.read_csv(self.csv_file, chunksize=500)

    def init(self):
        tick = self.mt5.copy_ticks_from(self.getSymbol(), self.time, 1, self.mt5.COPY_TICKS_ALL)
        dfTick = self.pd.DataFrame(tick)
        self.bid = dfTick['bid'].to_list()[0]
        self.ask = dfTick['ask'].to_list()[0]
        self.spread = (self.bid - self.ask) * 10000

    def increaseUnitTime(self):
        self.time += self.deltaTime
        tick = self.mt5.copy_ticks_from(self.getSymbol(), self.time, 1, self.mt5.COPY_TICKS_ALL)
        dfTick = self.pd.DataFrame(tick)
        self.bid = dfTick['bid'].to_list()[0]
        self.ask = dfTick['ask'].to_list()[0]
        self.spread = (self.bid - self.ask) * 10000
        if self.positionOpened:
            if self.positionType == self.mt5.ORDER_TYPE_BUY:
                self.profit = self.lot * (self.askOpen - self.bid) * 10000
            elif self.positionType == self.mt5.ORDER_TYPE_SELL:
                self.profit = self.lot * (self.bidOpen - self.ask) * 10000

    def getBar(self, timeFrame):
        #todo: fix this
        #d= self.pd.DataFrame.from_dict({'close':[0], 'open':[0]})
        #return d
        currencyBar = self.mt5.copy_rates_from(self.currencyPair, timeFrame, self.time, 1)
        currencyBar_frame = self.pd.DataFrame(currencyBar)
        currencyBar_frame['time']=self.pd.to_datetime(currencyBar_frame['time'], unit='s')
        return currencyBar_frame

    def positionClose(self, amount, orderType, orderNumber):
        self.profit = 0.0
        self.positionOpened = False
        return self.orderDone

    def positionOpen(self, amount, orderType):
        self.positionType = orderType
        self.lot = amount
        self.bidOpen = self.bid
        self.askOpen = self.ask
        self.positionOpened = True
        return self.orderDone

    def getProfitOnOpenPosition(self):
        return self.profit

    def getSpread(self):
        return self.spread

    def closeAllOpenPositions(self):
        return True