import datetime
import MetaTrader5 as mt5
import pandas as pd
import pytz
import os

currencyPair='GBPUSD'
startDateTime = '2020-08-10 00:00:00+00:00'
 
# establish connection to MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# set time zone to UTC
timezone = pytz.timezone("Etc/UTC")
# create 'datetime' object in UTC time zone to avoid the implementation of a local time zone offset
utc_from = datetime.datetime.fromisoformat(startDateTime)
startDateTimeStr = utc_from.strftime("%Y%m%d%H%M%S")
#delta_time = datetime.timedelta(seconds=86399)
delta_time = datetime.timedelta(days = 1)

try:
    while utc_from < datetime.datetime.now(datetime.timezone.utc):
        if utc_from.weekday() == 5 or utc_from.weekday() == 6:
            print('skipping:{}'.format(utc_from.strftime("%Y-%m-%d %H:%M:%S %A")))
            utc_from = utc_from + delta_time
            continue
        ticks = mt5.copy_ticks_range(currencyPair, utc_from, utc_from + delta_time, mt5.COPY_TICKS_ALL)
        
        ticks_frame=pd.DataFrame(ticks)
        # convert time in seconds into the datetime format
        ticks_frame['time']=pd.to_datetime(ticks_frame['time'], unit='s')
        #write fixed start and end points
        ticks_frame.iloc[0,ticks_frame.columns.get_loc('time')] = pd.Timestamp(utc_from.strftime('%Y-%m-%d %H:%M:%S'))
        endtime = datetime.datetime.combine(utc_from.date(),datetime.time(23,59,59))
        ticks_frame.iloc[-1,ticks_frame.columns.get_loc('time')] = pd.Timestamp(endtime.strftime('%Y-%m-%d %H:%M:%S'))
        # drop duplicates
        ticks_frame = ticks_frame.drop_duplicates(subset=['time'])

        #reindex
        ticks_frame = ticks_frame.set_index('time').resample('S').ffill().reset_index()

        fileName = currencyPair + '_' + utc_from.strftime("%Y%m%d") + '.csv'

        #remove if file already exists
        if os.path.exists(fileName):
            print('File {} already exit removing it'.format(fileName))
            os.remove(fileName)
        
        print('Start Writing to file {}'.format(fileName))
        ticks_frame.to_csv(fileName,index=False,mode='w',columns=['time','ask','bid'])
        print('Successfully written {}'.format(fileName))
        utc_from = utc_from + delta_time
except :
    raise