trial_list = ['GRB000911', 'GRB011121-SN2001ke','GRB020305','GRB020405','GRB020410','GRB020903','GRB021211-SN2002lt','GRB030723','GRB030725','GRB041006']

import pandas as pd
import sqlite3
import numpy as np
from astropy.time import Time

# Get the trigger time
def get_db_connection():
    conn = sqlite3.connect('Masterbase.db')
    conn.row_factory = sqlite3.Row
    return conn

# Return the trigtimes as full UTC times
def get_trigtime(event_id):
    # To determine if we need to search the db by SN or by GRB name
    conn = get_db_connection()
    if 'GRB' in event_id:
        #GRBs with SNs and without
        grb_name = event_id.split('-')[0][3:]

        # Table with triggertimes
        trigtable = conn.execute(
            'SELECT trigtime FROM TrigCoords WHERE grb_id=?', (grb_name,))

        # Extract the value from the cursor object
        for i in trigtable:
            trigtime = i[0]

        # Make it a full UTC time
        if np.float64(grb_name[:2])>90:
            trigtime = '19'+grb_name[:2]+'-'+grb_name[2:4]+'-'+grb_name[-2:]+'T'+trigtime
        else:
            trigtime = '20'+grb_name[:2]+'-'+grb_name[2:4]+'-'+grb_name[-2:]+'T'+trigtime

    # Lone SN cases
    elif 'SN' or 'AT' in event_id:
        sn_name = event_id[2:]

        # Table with triggertimes
        trigtable = conn.execute(
            'SELECT trigtime FROM TrigCoords WHERE sn_name=?', (sn_name,))

        # Extract the value from the cursor object
        for i in trigtable:
            trigtime = i[0]

    conn.close()
    return trigtime

# Dictionary to convert months to numbers
month2number = {'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04', 'May':'05', 'Jun':'06', 'Jul':'07', 'Aug':'08', 'Sep':'09', 'Oct':'10', 'Nov':'11', 'Dec':'12'}

# A function to turn decimal days into days, hours, minutes and seconds
def deciday(date):
    # The day is everything before the .
    l = float(date)
    day =  int(l)

    k = (l-float(day))*24
    hour = int(k)
    minute = np.floor((k*60) % 60)
    second = (k*3600) % 60

    # Make sure the days will match isotime format 2020-02-03T18:14:24 2004-11-02T07:11:59
    if day<10:
        day = '0'+str(day)
    if hour<10:
        hour = '0'+str(hour)
    if minute<10:
        minute = '0'+str(minute)
    if second<10:
        second = '0'+str(second)
    return(day, hour, minute, second)

# A function to parse date info. This will convert the date data to elapsed time since trigger.
def elapsed_time(dataframe, trigtime):
    # Handle the different date formats
    if dataframe['date_unit'][0] == "yyyy-month-deciday":
        time = list()
        for i in range(len(dataframe['date'])):
            date = dataframe['date'][i].split('-')
            year = date[0]
            month = month2number[date[1]]

            # Get the deciday to days, hours, min, sec
            day, hour, minute, second = deciday(date[2])

            # Turn into isotime
            isotime = str(year)+'-'+str(month)+'-'+str(day)+'T'+str(hour)+':'+str(minute)[:2]+':'+str(second)[:2]

            # astropy to subtract the two isotimes
            time_list = [isotime, trigtime]
            t = Time(time_list, format='isot', scale='utc')
            time.append(t[0]-t[1])
        dataframe['time'] = time

    # yyyy-mm-deciday-deciday
    if dataframe['date_unit'][0] == "yyyy-mm-deciday-deciday":
        time = list()
        for i in range(len(dataframe['date'])):
            date = dataframe['date'][i].split('-')
            year = date[0]
            month = date[1]

            # Get the deciday to days, hours, min, sec
            day1, hour1, minute1, second1 = deciday(date[2])
            day2, hour2, minute2, second2 = deciday(date[3])

            # Turn into isotime
            isotime1 = str(year)+'-'+str(month)+'-'+str(day1)+'T'+str(hour1)+':'+str(minute1)[:2]+':'+str(second1)[:2]
            isotime2 = str(year)+'-'+str(month)+'-'+str(day2)+'T'+str(hour2)+':'+str(minute2)[:2]+':'+str(second2)[:2]

            # astropy to subtract the two isotimes
            time_list = [isotime1, isotime2, trigtime]
            t = Time(time_list, format='isot', scale='utc')
            isotime = t[0]+((t[1]-t[0])/2)
            time.append(isotime-t[2])

        dataframe['time'] = time

    if dataframe['date_unit'][0] == "yyyy-month-deciday-deciday":
        time = list()
        for i in range(len(dataframe['date'])):
            date = dataframe['date'][i].split('-')
            year = date[0]
            month = month2number[date[1]]

            # Get the deciday to days, hours, min, sec
            day1, hour1, minute1, second1 = deciday(date[2])
            day2, hour2, minute2, second2 = deciday(date[3])

            # Turn into isotime
            isotime1 = str(year)+'-'+str(month)+'-'+str(day1)+'T'+str(hour1)+':'+str(minute1)[:2]+':'+str(second1)[:2]
            isotime2 = str(year)+'-'+str(month)+'-'+str(day2)+'T'+str(hour2)+':'+str(minute2)[:2]+':'+str(second2)[:2]

            # astropy to subtract the two isotimes
            time_list = [isotime1, isotime2, trigtime]
            t = Time(time_list, format='isot', scale='utc')
            isotime = t[0]+((t[1]-t[0])/2)
            time.append(isotime-t[2])

        dataframe['time'] = time
    
    return dataframe

data = pd.read_csv('./SourceData/GRB021211-SN2002lt/GRB021211-SN2002lt_Radio.txt', sep='\t')
new_data = elapsed_time(data, get_trigtime('GRB021211-SN2002lt'))
new_data.to_csv('./SourceData/GRB021211-SN2002lt/GRB021211-SN2002lt_Radio.txt', sep='\t', index=False)

			
		# elif str(i) = "yyyy-month-deciday-deciday":
			
		# elif str(i) = "yyyy-mm-dd-hh:mm-hh:mm":

		# elif str(i) = "MJD"