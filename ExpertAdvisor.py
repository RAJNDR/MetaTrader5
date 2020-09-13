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
        #selling pair
        self.sellPair = self.dict_args['sellingPair']
        self.timeFrame = self.dict_args['timeFrame']
        self.lotSize = self.dict_args['lotSize']
        self.profitMargin = self.dict_args['profitMargin']
        self.lossMargin = self.dict_args['lossMargin']
        self.spreadMargin = self.dict_args['spreadMargin']
        
        self.initSelf = True
        ##
        self.lastCloseBuyingPair = {}
        self.lastCloseSellingPair = {}
        ##
        self.instProfit = 0.0
        self.cumulativeProfit = 0.0
        self.openNewPosition = False
        self.closeOpenPositions = False
        ##
        self.openPositionBuying = {}
        self.openPositionSelling = {}
        ##
        self.closePositionBuying = {}
        self.closePositionSelling = {}
        ##
        self.openPositionBuyingOrderNumber = {}
        self.openPositionSellingOrderNumber = {}
        for pair in self.sellPair:
            self.openPositionSelling[pair.getSymbol()] = None
            self.closePositionSelling[pair.getSymbol()] = None
            self.openPositionSellingOrderNumber[pair.getSymbol()] = 0

        for pair in self.buyPair:
            self.openPositionBuying[pair.getSymbol()] = None
            self.closePositionBuying[pair.getSymbol()] = None
            self.openPositionBuyingOrderNumber[pair.getSymbol()] = 0

        ##
        self.lastInstProfitBuying = {}
        self.lastInstProfitSelling = {}

    def prepareAdvisor(self):
        return

    def getAdvisorProfit(self):
        return self.cumulativeProfit

    def runAdvisor(self):
        #get bars of currency pairs
        barBuyingPair = {}
        for pair in self.buyPair:
            barBuyingPair[pair.getSymbol()] = pair.getBar(self.timeFrame)
        barSellingPair = {}
        for pair in self.sellPair:
            barSellingPair[pair.getSymbol()] = pair.getBar(self.timeFrame)
        #get closing prices
        closeBuyingPair={}
        closeSellingPair={}
        for key,value in barBuyingPair.items():
            closeBuyingPair[key] = value['close'].to_list()[0]
        for key,value in barSellingPair.items():
            closeSellingPair[key] = value['close'].to_list()[0]
        #run only onetime
        if self.initSelf:
            self.initSelf = False
            self.lastCloseBuyingPair = closeBuyingPair
            self.lastCloseSellingPair = closeSellingPair

        #calculate PIP
        pipBuyingPair = {}
        pipSellingPair = {}
        for pair in self.buyPair:
            pipBuyingPair[pair.getSymbol()] = closeBuyingPair[pair.getSymbol()] - self.lastCloseBuyingPair[pair.getSymbol()]
        
        for pair in self.sellPair:
            pipSellingPair[pair.getSymbol()] = closeSellingPair[pair.getSymbol()] - self.lastCloseSellingPair[pair.getSymbol()]
        #inst Profit
        instProfitBuyingPair={}
        for pair in self.buyPair:
            instProfitBuyingPair[pair.getSymbol()] = pair.getProfitOnOpenPosition()

        instProfitSellingPair={}
        for pair in self.sellPair:
            instProfitSellingPair[pair.getSymbol()] = pair.getProfitOnOpenPosition()
        #instProfit calc
        self.instProfit = sum(instProfitSellingPair.values()) + sum(instProfitBuyingPair.values())

        self.lastInstProfitBuying = instProfitBuyingPair
        self.lastInstProfitSelling = instProfitSellingPair

        for pair in self.buyPair:
            self.logger.info("Pair:{},Order:{},Open:{},Close:{},PipChange:{},ProfitInst:{},ProfitCombined:{},ProfitCumm:{}".format(pair.getSymbol(), self.openPositionBuyingOrderNumber[pair.getSymbol()],barBuyingPair[pair.getSymbol()]['open'].to_list()[0],barBuyingPair[pair.getSymbol()]['close'].to_list()[0],pipBuyingPair[pair.getSymbol()],instProfitBuyingPair[pair.getSymbol()],self.instProfit,self.cumulativeProfit))
        
        for pair in self.sellPair:
            self.logger.info("Pair:{},Order:{},Open:{},Close:{},PipChange:{},ProfitInst:{},ProfitCombined:{},ProfitCumm:{}".format(pair.getSymbol(), self.openPositionSellingOrderNumber[pair.getSymbol()],barSellingPair[pair.getSymbol()]['open'].to_list()[0],barSellingPair[pair.getSymbol()]['close'].to_list()[0],pipSellingPair[pair.getSymbol()],instProfitSellingPair[pair.getSymbol()],self.instProfit,self.cumulativeProfit))

        #set bool to open Position
        if all(x is None for x in self.openPositionBuying.values()) and all(x is None for x in self.openPositionSelling.values()):
            #if (self.buyPair.getRSI(14) >= 70.0) and (self.middlePair.getRSI(14) >= 70.0) and (self.sellPair.getRSI(14) <= 30.0):
            self.openNewPosition = True
        #Open position
        if self.openNewPosition:
            #Try to open position
            self.openPositionBuyingOrderNumber = dict.fromkeys(self.openPositionBuyingOrderNumber, 0)
            self.openPositionSellingOrderNumber = dict.fromkeys(self.openPositionSellingOrderNumber, 0)
            self.openNewPosition = False
            #close any open position
            if all(x.closeAllOpenPositions() is True for x in self.sellPair) and all(x.closeAllOpenPositions() is True for x in self.buyPair):
                self.logger.warning("No position are open. Opening new Position")
            else:
                self.logger.error("Cannot close already open positions! wait till next cycle.")
                return
            #check Spread
            #totalSpread = self.sellPair.getSpread() + self.buyPair.getSpread()
            totalSpread = sum([pair.getSpread() for pair in self.buyPair]) + sum([pair.getSpread() for pair in self.sellPair])
            if (totalSpread) < self.spreadMargin:
                msg = str()
                allPairs = self.sellPair + self.buyPair
                for pair in allPairs:
                    msg += "Spread{}:{},".format(pair.getSymbol(),pair.getSpread())
                msg += "totalSpread:{},Threshold:{}".format(totalSpread,self.spreadMargin)
                #self.logger.error("Spread{}:{},Spread{}:{},Spread{}:{},totalSpread:{},Threshold:{}".format(self.sellPair.getSymbol(),self.sellPair.getSpread(),self.middlePair.getSymbol(),self.middlePair.getSpread(),self.buyPair.getSymbol(),self.buyPair.getSpread(),totalSpread,self.spreadMargin))
                self.logger.error(msg)
                return
            
            for pair in self.sellPair:
                self.logger.warning("Opening {} with spread:{},totalSpread:{},Threshold:{}".format(pair.getSymbol(),pair.getSpread(),totalSpread,self.spreadMargin))
            for pair in self.buyPair:
                self.logger.warning("Opening {} with spread:{},totalSpread:{},Threshold:{}".format(pair.getSymbol(),pair.getSpread(),totalSpread,self.spreadMargin))
            #opening position
            for pair in self.buyPair:
                self.openPositionBuying[pair.getSymbol()] = pair.positionOpen(self.lotSize,self.mt5.ORDER_TYPE_BUY)
            for pair in self.sellPair:
                self.openPositionSelling[pair.getSymbol()] = pair.positionOpen(self.lotSize,self.mt5.ORDER_TYPE_SELL)

            if all(x is None for x in self.openPositionBuying.values()) or all(x is None for x in self.openPositionSelling.values()):
                self.logger.error('Transaction not successfull! wait till next.')
                self.openPositionBuying = dict.fromkeys(self.openPositionBuying, None)
                self.openPositionSelling = dict.fromkeys(self.openPositionSelling, None)
                return

            if all(x.retcode != self.mt5.TRADE_RETCODE_DONE for key,x in self.openPositionBuying.items()) or all(x.retcode != self.mt5.TRADE_RETCODE_DONE for key,x in self.openPositionSelling.items()):
                allPairs = {**self.openPositionBuying , **self.openPositionSelling}
                for key,value in allPairs.items():
                    self.logger.error("OpenPosition:{} exit with Ret code {} and comment {}".format(key,value.retcode,value.comment))
                self.openPositionBuying = dict.fromkeys(self.openPositionBuying, None)
                self.openPositionSelling = dict.fromkeys(self.openPositionSelling, None)
                return
            self.openPositionBuyingOrderNumber = {key:pair.order for key,pair in self.openPositionBuying.items()}
            self.openPositionSellingOrderNumber = {key:pair.order for key,pair in self.openPositionSelling.items()}
            self.logger.warning("POSITION OPEN!")

        #set bool to close position if profit goes out of margin
        if (self.instProfit > self.profitMargin) or (self.instProfit < self.lossMargin):
            self.closeOpenPositions = True

        #Close position
        if self.closeOpenPositions:
            self.closeOpenPositions = False
            if all(x is None for x in self.openPositionBuying.values()) and all(x is None for x in self.openPositionSelling.values()):
                self.logger.error('No position Available to close')
                return
            
            #close Positions individual pairs
            for pair in self.buyPair:
                self.closePositionBuying[pair.getSymbol()] = pair.positionClose(self.lotSize,self.mt5.ORDER_TYPE_SELL,self.openPositionBuying[pair.getSymbol()].order)
            for pair in self.sellPair:
                self.closePositionSelling[pair.getSymbol()] = pair.positionClose(self.lotSize,self.mt5.ORDER_TYPE_BUY,self.openPositionSelling[pair.getSymbol()].order)

            self.openPositionBuying = dict.fromkeys(self.openPositionBuying, None)
            self.openPositionSelling = dict.fromkeys(self.openPositionSelling, None)

            #start editing this
            if all(x is None for x in self.closePositionBuying.values()) or all(x is None for x in self.closePositionSelling.values()):
                self.logger.error('Position Closing not successfull! wait till next.')
                return

            if all(x.retcode != self.mt5.TRADE_RETCODE_DONE for key,x in self.closePositionBuying.items()) or all(x.retcode != self.mt5.TRADE_RETCODE_DONE for key,x in self.closePositionSelling.items()):
                allPairs = {**self.closePositionBuying , **self.closePositionSelling}
                for key,value in allPairs.items():
                    self.logger.error("ClosePosition:{} exit with Ret code {} and comment {}".format(key,value.retcode,value.comment))
                
                self.openNewPosition = True
                return

            self.cumulativeProfit += sum(self.lastInstProfitBuying.values()) + sum(self.lastInstProfitSelling.values())

            self.closePositionBuying = dict.fromkeys(self.closePositionBuying, None)
            self.closePositionSelling = dict.fromkeys(self.closePositionSelling, None)
            self.logger.warning("POSITION CLOSE! at CummulativeProfit: {}".format(self.cumulativeProfit))
        #set variable for previous cycle
        self.lastCloseBuyingPair = closeBuyingPair
        self.lastCloseSellingPair = closeSellingPair

    def getSellPair(self):
        return self.sellPair

    def getBuyPair(self):
        return self.buyPair

    def getMiddlePair(self):
        return self.middlePair