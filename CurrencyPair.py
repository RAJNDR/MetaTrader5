class CurrencyPair:
    def __init__(self,currencyPair, mt5, pd):
        self.currencyPair = currencyPair
        self.mt5 = mt5
        self.pd = pd

    def getSymbol(self):
        return self.currencyPair

    def getBar(self, timeFrame):
        currencyBar = self.mt5.copy_rates_from_pos(self.currencyPair, timeFrame, 0, 1)
        currencyBar_frame = self.pd.DataFrame(currencyBar)
        currencyBar_frame['time']=self.pd.to_datetime(currencyBar_frame['time'], unit='s')
        return currencyBar_frame

    def positionClose(self, amount, orderType, orderNumber):
        if orderType == self.mt5.ORDER_TYPE_BUY:
            price = self.mt5.symbol_info_tick(self.currencyPair).ask
        elif orderType == self.mt5.ORDER_TYPE_SELL:
            price = self.mt5.symbol_info_tick(self.currencyPair).bid

        request={
            "action": self.mt5.TRADE_ACTION_DEAL,
            "symbol": self.currencyPair,
            "volume": amount,
            "type": orderType,
            "position": orderNumber,
            "price": price,
            "deviation": 1,
            "magic": 234000,
            "comment": "python script close",
            "type_time": self.mt5.ORDER_TIME_GTC,
            "type_filling": self.mt5.ORDER_FILLING_RETURN,
        }
        result = self.mt5.order_send(request)
        return result


    def positionOpen(self, amount, orderType):
        if orderType == self.mt5.ORDER_TYPE_BUY:
            price = self.mt5.symbol_info_tick(self.currencyPair).ask
        elif orderType == self.mt5.ORDER_TYPE_SELL:
            price = self.mt5.symbol_info_tick(self.currencyPair).bid

        request = {
            "action": self.mt5.TRADE_ACTION_DEAL,
            "symbol":  self.currencyPair,
            "volume": amount,
            "type": orderType,
            "price": price,
            "sl": 0.0,
            "tp": 0.0,
            "deviation": 1,
            "magic": 234000,
            "comment": "python script open",
            "type_time": self.mt5.ORDER_TIME_GTC,
            "type_filling": self.mt5.ORDER_FILLING_RETURN,
        }
        result = self.mt5.order_send(request)
        return result

    def getProfitOnOpenPosition(self):
        openPosition = self.mt5.positions_get(symbol=self.currencyPair)
        if len(openPosition) == 0:
            instProfit = 0
        else:
            instProfit = openPosition[0].profit
        return instProfit

    def getSpread(self):
        askPrice = self.mt5.symbol_info_tick(self.currencyPair).ask
        bidPrice = self.mt5.symbol_info_tick(self.currencyPair).bid
        spreadInPips = (bidPrice - askPrice) * 10000
        return spreadInPips