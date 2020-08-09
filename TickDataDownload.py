import datetime
import MetaTrader5 as mt5
import pandas as pd
import pytz
import os

currencyPair='GBPUSD'
timeStep=[1,0,0] #Days, Hours, Minutes
startDateTime = '2020-08-07 00:00:00+00:00'
useGenDateTime = True # false to use date from mt5
 
# establish connection to MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# set time zone to UTC
timezone = pytz.timezone("Etc/UTC")
# create 'datetime' object in UTC time zone to avoid the implementation of a local time zone offset
#utc_from = datetime.datetime(2017, 1, 1, 8, 0,tzinfo=timezone)
utc_from = datetime.datetime.fromisoformat(startDateTime)
delta_time = datetime.timedelta(days = timeStep[0], hours = timeStep[1], minutes=timeStep[2])
header_once = True
fileName = currencyPair + '_' + utc_from.strftime("%Y%m%d%H%M%S") +"_"+ "{}{}{}".format(timeStep[0],timeStep[1],timeStep[2]) + ".csv"
#remove if file already exists
if os.path.exists(fileName):
    print('File {} already exit removing it'.format(fileName))
    os.remove(fileName)
print('Start Writing to file {}'.format(fileName))
try:
    while utc_from < datetime.datetime.now(datetime.timezone.utc):
        ticks = mt5.copy_ticks_from(currencyPair, utc_from, 1, mt5.COPY_TICKS_ALL)
        #bars = mt5.copy_rates_from("GBPCHF", mt5.TIMEFRAME_M2,utc_from,1)
        #print(bars)
        ticks_frame=pd.DataFrame(ticks)
        bid = ticks_frame['bid'].to_list()[0]
        ask = ticks_frame['ask'].to_list()[0]
        # convert time in seconds into the datetime format
        if useGenDateTime:
            #ticks_frame['date'] = utc_from.date().isoformat()
            ticks_frame.insert(0,'date',utc_from.date().isoformat())
            ticks_frame['time'] = utc_from.time().isoformat()
        else:
            mt5_dt=pd.to_datetime(ticks_frame['time'], unit='s')
            #ticks_frame['date'] = mt5_dt.date().isoformat()
            ticks_frame.insert(0,'date',mt5_dt.date().isoformat())
            ticks_frame['time'] = mt5_dt.time().isoformat()
        
        ticks_frame.to_csv(fileName,index=False,mode='a',header=header_once)
        header_once = False
        print(ticks_frame.head(10))
        utc_from = utc_from + delta_time
except :
    pass