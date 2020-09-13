import datetime
import MetaTrader5 as mt5
import pandas as pd

class TickData:
    def __init__(self,symbol,mt5,pd):
        self.symbol = symbol
        self.deltatime = datetime.timedelta(days=1)
        self.currentDateTime = datetime.datetime(1970,1,1)
        self.mt5 = mt5
        self.pd = pd
        self.df = None
        self.historicalDatasize = self.deltatime

    def getTick(self,dateTime):
        if self.currentDateTime is None:
            self.currentDateTime = dateTime

        while self.currentDateTime.weekday() == 5 or self.currentDateTime.weekday() == 6:
            self.currentDateTime = self.currentDateTime + self.deltatime

        if self.currentDateTime.date() != dateTime.date():
            ticks = self.mt5.copy_ticks_range(self.symbol, dateTime, dateTime + self.deltatime, mt5.COPY_TICKS_ALL)
            df = self.pd.DataFrame(ticks)
            df['time']=self.pd.to_datetime(df['time'], unit='s')
            df = df[['time','bid','ask']]
            df.iloc[0,df.columns.get_loc('time')] = self.pd.Timestamp(dateTime.strftime('%Y-%m-%d %H:%M:%S'))
            endtime = datetime.datetime.combine(dateTime.date(),datetime.time(23,59,59))
            df.iloc[-1,df.columns.get_loc('time')] = self.pd.Timestamp(endtime.strftime('%Y-%m-%d %H:%M:%S'))
            df = df.drop_duplicates(subset=['time'])
            df = df.set_index('time').resample('S').ffill().reset_index()
            df = df.set_index('time')
            if self.df is None:
                self.df = df
            else:
                frames = [self.df, df]
                currentlength = len(self.df)
                self.df= pd.concat(frames)
                if len(self.df) >= 2*currentlength:
                    self.df = self.df.iloc[len(df):]
        
        self.currentDateTime = dateTime
        bidPrice = self.df.loc[self.currentDateTime.strftime('%Y-%m-%d %H:%M:%S'),'bid']
        askPrice = self.df.loc[self.currentDateTime.strftime('%Y-%m-%d %H:%M:%S'),'ask']
        time = self.currentDateTime
        return (time,bidPrice,askPrice)

    def getDataFrame(self):
        return self.df
        

if __name__ == '__main__':
    if not mt5.initialize():
        print("initialize() failed, error code =" + mt5.last_error()[2])
        mt5.shutdown()
    print('Hello')
    td = TickData('GBPUSD',mt5,pd)
    startDateTime = '2020-08-10 10:12:00+00:00'
    utc_from = datetime.datetime.fromisoformat(startDateTime)
    print(td.getTick(utc_from))
    startDateTime = '2020-08-10 11:12:00+00:00'
    utc_from = datetime.datetime.fromisoformat(startDateTime)
    print(td.getTick(utc_from))
    startDateTime = '2020-08-11 11:12:00+00:00'
    utc_from = datetime.datetime.fromisoformat(startDateTime)
    print(td.getTick(utc_from))
    startDateTime = '2020-08-11 11:12:01+00:00'
    utc_from = datetime.datetime.fromisoformat(startDateTime)
    print(td.getTick(utc_from))
