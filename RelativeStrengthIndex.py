import pandas as pd
import MetaTrader5 as mt5
import matplotlib.pyplot as plt

class RelativeStrengthIndex:
    def __init__(self,df):
        self.window_length = 14
        self.df = df

    def getEWMBasedRSI(self):
        delta = self.df.diff()
        # Get rid of the first row, which is NaN since it did not have a previous 
        # row to calculate the differences
        delta = delta[1:] 

        # Make the positive gains (up) and negative gains (down) Series
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0

        # Calculate the EWMA
        roll_up1 = up.ewm(span=self.window_length).mean()
        roll_down1 = down.abs().ewm(span=self.window_length).mean()

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
        RSI.plot()
        plt.show()
        return RSI

if __name__ == '__main__':
    print("Hello")

    if not mt5.initialize():
        print("initialize() failed, error code =",mt5.last_error())
        quit()

    rates = mt5.copy_rates_from_pos("GBPCHF", mt5.TIMEFRAME_M1, 0, 100)
    rates_frame = pd.DataFrame(rates)
    rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
    rsi = RelativeStrengthIndex(rates_frame['close'])
    print("getSMABasedRSI:{}".format(rsi.getSMABasedRSI()))
    print("getEWMBasedRSI:{}".format(rsi.getEWMBasedRSI()))
    