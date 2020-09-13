import pandas as pd
import pandas_ta as ta
import MetaTrader5 as mt5
import matplotlib.pyplot as plt
import stockstats


class RelativeStrengthIndex:
    def __init__(self,df):
        self.window_length = 14
        self.df = df

    def getEWMBasedRSI(self):
        self.df.set_index('time')
        self.df.sort_index()
        delta = self.df['close'].diff()
        # Get rid of the first row, which is NaN since it did not have a previous 
        # row to calculate the differences
        delta = delta[1:] 

        # Make the positive gains (up) and negative gains (down) Series
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0

        # Calculate the EWMA
        roll_up1 = up.ewm(span=self.window_length,adjust=True).mean()
        roll_down1 = down.abs().ewm(span=self.window_length,adjust=True).mean()

        # Calculate the RSI based on EWMA
        RS = roll_up1 / roll_down1
        RSI = 100.0 - (100.0 / (1.0 + RS))
        RSI.plot()
        plt.show()
        return RSI

    def getSMABasedRSI(self):
        delta = self.df.diff()
        # Get rid of the first row, which is NaN since it did not have a previous 
        # row to calculate the differences
        delta = delta[1:] 

        # Make the positive gains (up) and negative gains (down) Series
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0

        # Calculate the SMA
        roll_up2 = up.rolling(self.window_length).mean()
        roll_down2 = down.abs().rolling(self.window_length).mean()

        # Calculate the RSI based on SMA
        RS = roll_up2 / roll_down2
        RSI = 100.0 - (100.0 / (1.0 + RS))
        #RSI.plot()
        #plt.show()
        return RSI

    def rsiLibrary(self):
        roll_up2 = (self.df + self.df.abs()) / 2
        roll_down2 = (-self.df + self.df.abs()) / 2
        rs = roll_up2 / roll_down2
        rsi = 100 - 100 / (1.0 + rs)
        #rsi.plot()
        #plt.show()   
        return rsi    

if __name__ == '__main__':
    print("Hello")

    if not mt5.initialize():
        print("initialize() failed, error code =",mt5.last_error())
        quit()

    rates = mt5.copy_rates_from_pos("GBPCHF", mt5.TIMEFRAME_M1, 0, 100)
    rates_frame = pd.DataFrame(rates)
    #stock = stockstats.StockDataFrame.retype(rates_frame)
    #rsi = stock['rsi_14']
    result = rates_frame.ta.rsi(length = 14)
    result = rates_frame.ta.bbands(length=20,std=2)
    result.plot()
    #plt.ylim([0,100])
    plt.grid()
    plt.show()
    #rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
    #rsi = RelativeStrengthIndex(rates_frame[['time','close']])
    #print("getSMABasedRSI:{}".format(rsi.getSMABasedRSI()))
    #print("getEWMBasedRSI:{}".format(rsi.getEWMBasedRSI()))
    #print("rsiLibrary:{}".format(rsi.rsiLibrary()))
    