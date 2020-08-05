from CurrencyPair import CurrencyPair
import datetime

class ResultPosition:
    retCode = 0
    commit = ''
    def __init__(self):
        return


class SimCurrencyPair(CurrencyPair):
    def __init__(self,currencyPair, mt5, pd,logger,startTime,deltaTime):
        super().__init__(currencyPair,mt5,pd,logger)
        self.time = startTime
        self.deltaTime = deltaTime
        self.bid = 0.0
        self.ask = 0.0
        self.spread = 0.0

    def increaseUnitTime(self):
        self.time += self.deltaTime
        tick = self.mt5.copy_ticks_from(self.getSymbol(), self.time, 1, mt5.COPY_TICKS_ALL)
        dfTick = self.pd.DataFrame(tick)
        self.bid = dfTick['bid'].to_list()[0]
        self.ask = dfTick['ask'].to_list()[0]
        self.spread = (self.bid - self.ask) * 10000

    def getBar(self, timeFrame):
        currencyBar = self.mt5.copy_rates_from(self.currencyPair, timeFrame, self.time, 1)
        currencyBar_frame = self.pd.DataFrame(currencyBar)
        currencyBar_frame['time']=self.pd.to_datetime(currencyBar_frame['time'], unit='s')
        return currencyBar_frame

    def positionClose(self, amount, orderType, orderNumber):
        return

    def positionOpen(self, amount, orderType):
        return

    def getProfitOnOpenPosition(self):
        return

    def getSpread(self):
        return self.spread

    def closeAllOpenPositions(self):
        return True
