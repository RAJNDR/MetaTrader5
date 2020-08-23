class ExpertAdvisor:
    def __init__(self,dict_args,logger,mt5):
        self.dict_args = dict()
        self.dict_args = dict_args
        self.logger = logger
        self.mt5 = mt5

    def runAdvisor(self):
        return

    def prepareAdvisor(self):
        return

class HedgedPairAdvisor(ExpertAdvisor):
    def __init__(self,dict_args,logger,mt5):
        super().__init__(dict_args,logger,mt5)
        #buying pair
        self.buyPair = self.dict_args['buyingPair']
        #middle pair
        self.middlePair = self.dict_args['middlePair']
        self.middlePositionType = self.dict_args['middlePosition']
        #selling pair
        self.sellPair = self.dict_args['sellingPair']
        self.timeFrame = self.dict_args['timeFrame']
        self.lotSize = self.dict_args['lotSize']
        self.profitMargin = self.dict_args['profitMargin']
        self.lossMargin = self.dict_args['lossMargin']
        self.spreadMargin = self.dict_args['spreadMargin']
        
        self.initSelf = True
        ##
        self.lastCloseBuyingPair = 0.0
        self.lastCloseMiddlePair = 0.0
        self.lastCloseSellingPair = 0.0
        ##
        self.instProfit = 0.0
        self.cumulativeProfit = 0.0
        self.openNewPosition = False
        self.closeOpenPositions = False
        ##
        self.openPositionBuying = None
        self.openPositionMiddle = None 
        self.openPositionSelling = None
        ##
        self.closePositionBuying = None
        self.closePositionMiddle = None
        self.closePositionSelling = None
        ##
        self.lastInstProfitBuying = 0.0
        self.lastInstProfitMiddle = 0.0
        self.lastInstProfitSelling = 0.0
        ##
        self.openPositionBuyingOrderNumber = 0
        self.openPositionMiddleOrderNumber = 0
        self.openPositionSellingOrderNumber = 0

    def prepareAdvisor(self):
        return

    def getAdvisorProfit(self):
        return self.cumulativeProfit

    def runAdvisor(self):
        #get bars of currency pairs
        barBuyingPair = self.buyPair.getBar(self.timeFrame)
        barMiddlePair = self.middlePair.getBar(self.timeFrame)
        barSellingPair = self.sellPair.getBar(self.timeFrame)
        #get closing prices
        closeBuyingPair = barBuyingPair['close'].to_list()[0]
        closeMiddlePair = barMiddlePair['close'].to_list()[0]
        closeSellingPair = barSellingPair['close'].to_list()[0]
        #run only onetime
        if self.initSelf:
            self.initSelf = False
            self.lastCloseBuyingPair = closeBuyingPair
            self.lastCloseMiddlePair = closeMiddlePair
            self.lastCloseSellingPair = closeSellingPair

        #calculate PIP
        pipBuyingPair = closeBuyingPair - self.lastCloseBuyingPair
        pipMiddlePair = closeMiddlePair - self.lastCloseMiddlePair
        pipSellingPair = closeSellingPair - self.lastCloseSellingPair
        #inst Profit
        instProfitBuyingPair = self.buyPair.getProfitOnOpenPosition()
        instProfitMiddlePair = self.middlePair.getProfitOnOpenPosition()
        instProfitSellingPair = self.sellPair.getProfitOnOpenPosition()
        #instProfit calc
        self.instProfit = instProfitSellingPair + instProfitBuyingPair + instProfitMiddlePair
        self.lastInstProfitBuying = instProfitBuyingPair
        self.lastInstProfitMiddle = instProfitMiddlePair
        self.lastInstProfitSelling = instProfitSellingPair

        self.logger.info("Pair:{},Order:{},Open:{},Close:{},PipChange:{},ProfitInst:{},ProfitCombined:{},ProfitCumm:{}".format(self.buyPair.getSymbol(), self.openPositionBuyingOrderNumber,barBuyingPair['open'].to_list()[0],barBuyingPair['close'].to_list()[0],pipBuyingPair,instProfitBuyingPair,self.instProfit,self.cumulativeProfit))
        self.logger.info("Pair:{},Order:{},Open:{},Close:{},PipChange:{},ProfitInst:{},ProfitCombined:{},ProfitCumm:{}".format(self.middlePair.getSymbol(), self.openPositionMiddleOrderNumber,barMiddlePair['open'].to_list()[0],barMiddlePair['close'].to_list()[0],pipMiddlePair,instProfitMiddlePair,self.instProfit,self.cumulativeProfit))
        self.logger.info("Pair:{},Order:{},Open:{},Close:{},PipChange:{},ProfitInst:{},ProfitCombined:{},ProfitCumm:{}".format(self.sellPair.getSymbol(), self.openPositionSellingOrderNumber,barSellingPair['open'].to_list()[0],barSellingPair['close'].to_list()[0],pipSellingPair,instProfitSellingPair,self.instProfit,self.cumulativeProfit))

        #set bool to open Position
        if self.openPositionBuying is None and self.openPositionSelling is None:
            #if (self.instProfit >= 0.0):
            self.openNewPosition = True

        #Open position
        if self.openNewPosition:
            #Try to open position
            self.openPositionBuyingOrderNumber = 0
            self.openPositionMiddleOrderNumber = 0
            self.openPositionSellingOrderNumber = 0
            self.openNewPosition = False
            #close any open position
            if self.sellPair.closeAllOpenPositions() and self.middlePair.closeAllOpenPositions() and self.buyPair.closeAllOpenPositions():
                self.logger.warning("No position are open. Opening new Position")
            else:
                self.logger.error("Cannot close already open positions! wait till next cycle.")
                return
            #check Spread
            totalSpread = self.sellPair.getSpread() + self.middlePair.getSpread() + self.buyPair.getSpread()
            if (totalSpread) < self.spreadMargin:
                self.logger.error("Spread{}:{},Spread{}:{},Spread{}:{},totalSpread:{},Threshold:{}".format(self.sellPair.getSymbol(),self.sellPair.getSpread(),self.middlePair.getSymbol(),self.middlePair.getSpread(),self.buyPair.getSymbol(),self.buyPair.getSpread(),totalSpread,self.spreadMargin))
                return
            self.logger.warning("Opening{} with spread:{},totalSpread:{},Threshold:{}".format(self.sellPair.getSymbol(),self.sellPair.getSpread(),totalSpread,self.spreadMargin))
            self.logger.warning("Opening{} with spread:{},totalSpread:{},Threshold:{}".format(self.middlePair.getSymbol(),self.middlePair.getSpread(),totalSpread,self.spreadMargin))
            self.logger.warning("Opening{} with spread:{},totalSpread:{},Threshold:{}".format(self.buyPair.getSymbol(),self.buyPair.getSpread(),totalSpread,self.spreadMargin))
            #opening position
            self.openPositionBuying = self.buyPair.positionOpen(self.lotSize,self.mt5.ORDER_TYPE_BUY)
            if self.middlePositionType.lower() == 'buying':
                self.openPositionMiddle = self.middlePair.positionOpen(self.lotSize,self.mt5.ORDER_TYPE_BUY)
            else:
                self.openPositionMiddle = self.middlePair.positionOpen(self.lotSize,self.mt5.ORDER_TYPE_SELL)
            self.openPositionSelling = self.sellPair.positionOpen(self.lotSize,self.mt5.ORDER_TYPE_SELL)

            if self.openPositionBuying is None or self.openPositionMiddle is None or self.openPositionSelling is None:
                self.logger.error('Transaction not successfull! wait till next.')
                self.openPositionBuying = None
                self.openPositionMiddle = None
                self.openPositionSelling = None
                return

            if (self.openPositionBuying.retcode != self.mt5.TRADE_RETCODE_DONE) or (self.openPositionMiddle.retcode != self.mt5.TRADE_RETCODE_DONE) or (self.openPositionSelling.retcode != self.mt5.TRADE_RETCODE_DONE):
                self.logger.error("openPositionBuying exit with Ret code {} and comment {}".format(self.openPositionBuying.retcode,self.openPositionBuying.comment))
                self.logger.error("openPositionMiddle exit with Ret code {} and comment {}".format(self.openPositionMiddle.retcode,self.openPositionMiddle.comment))
                self.logger.error("openPositionSelling exit with Ret code {} and comment {}".format(self.openPositionSelling.retcode,self.openPositionSelling.comment))
                self.openPositionBuying = None
                self.openPositionMiddle = None
                self.openPositionSelling = None
                return
            self.openPositionBuyingOrderNumber = self.openPositionBuying.order
            self.openPositionMiddleOrderNumber = self.openPositionMiddle.order
            self.openPositionSellingOrderNumber = self.openPositionSelling.order
            self.logger.warning("POSITION OPEN!")

        #set bool to close position if profit goes out of margin
        if (self.instProfit > self.profitMargin) or (self.instProfit < self.lossMargin):
            self.closeOpenPositions = True

        #Close position
        if self.closeOpenPositions:
            self.closeOpenPositions = False
            if (self.openPositionBuying is None) or (self.openPositionMiddle is None) or (self.openPositionSelling is None):
                self.logger.error('No position Available to close')
                return
            
            #close Positions individual pairs
            self.closePositionBuying = self.buyPair.positionClose(self.lotSize,self.mt5.ORDER_TYPE_SELL,self.openPositionBuying.order)
            if self.middlePositionType.lower() == 'buying':
                self.closePositionMiddle = self.middlePair.positionClose(self.lotSize,self.mt5.ORDER_TYPE_SELL,self.openPositionMiddle.order)
            else:
                self.closePositionMiddle = self.middlePair.positionClose(self.lotSize,self.mt5.ORDER_TYPE_BUY,self.openPositionMiddle.order)
            self.closePositionSelling = self.sellPair.positionClose(self.lotSize,self.mt5.ORDER_TYPE_BUY,self.openPositionSelling.order)
            self.openPositionBuying = None
            self.openPositionMiddle = None
            self.openPositionSelling = None

            if self.closePositionBuying is None or self.closePositionMiddle is None or self.closePositionSelling is None:
                self.logger.error('Position Closing not successfull! wait till next.')
                return

            if (self.closePositionBuying.retcode != self.mt5.TRADE_RETCODE_DONE) or (self.closePositionMiddle.retcode != self.mt5.TRADE_RETCODE_DONE) or (self.closePositionSelling.retcode != self.mt5.TRADE_RETCODE_DONE):
                self.logger.error("closePositionBuying exit with Ret code {} and comment {}".format(self.closePositionBuying.retcode,self.closePositionBuying.comment))
                self.logger.error("closePositionMiddle exit with Ret code {} and comment {}".format(self.closePositionMiddle.retcode,self.closePositionMiddle.comment))
                self.logger.error("closePositionSelling exit with Ret code {} and comment {}".format(self.closePositionSelling.retcode,self.closePositionSelling.comment))
                self.openNewPosition = True
                return

            self.cumulativeProfit += self.lastInstProfitBuying + self.lastInstProfitMiddle + self.lastInstProfitSelling

            self.closePositionBuying = None
            self.closePositionMiddle = None
            self.closePositionSelling = None
            self.logger.warning("POSITION CLOSE! at CummulativeProfit: {}".format(self.cumulativeProfit))
        #set variable for previous cycle
        self.lastCloseBuyingPair = closeBuyingPair
        self.lastCloseMiddlePair = closeMiddlePair
        self.lastCloseSellingPair = closeSellingPair

    def getSellPair(self):
        return self.sellPair

    def getBuyPair(self):
        return self.buyPair

    def getMiddlePair(self):
        return self.middlePair