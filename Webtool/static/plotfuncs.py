'''
This file converts any text file in the webtool SourceData folder into a standard format.
'''

import sqlite3
import glob
import os
import numpy as np
from astropy.time import Time
import pandas as pd

def list_grbs_with_data():
    """
    List of GRB-SNe that I have text file data on so far.
    """
    os.chdir("SourceData/")
    root = os.getcwd()
    dirs = [ item for item in os.listdir(root) if os.path.isdir(os.path.join(root, item))]

    event_list = []
    for i in dirs:
        if 'GRB' in str(i) or 'SN' in str(i):
            event_list.append(i)
    os.chdir('..')

    return event_list

event_list = list_grbs_with_data()

def get_db_connection():
    """
    Connect to the database.
    """
    conn = sqlite3.connect('Masterbase.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_trigtime(event_id):
    """
    Return the trigtimes as full UTC times
    """
    # To determine if we need to search the db by SN or by GRB name
    conn = get_db_connection()
    if 'GRB' in event_id:
        #GRBs with SNs and without
        grb_name = event_id.split('-', maxsplit=1)[0][3:]

        # Table with triggertimes
        trigtable = conn.execute(
            'SELECT trigtime FROM TrigCoords WHERE grb_id=?', (grb_name,))

        # Extract the value from the cursor object
        for i in trigtable:
            if i[0] is not None:
                trigtime = i[0]

                # Make it a full UTC time
                if np.float64(grb_name[:2])>90:
                    trigtime = '19'+grb_name[:2]+'-'+grb_name[2:4]+'-'+grb_name[-2:]+'T'+trigtime
                else:
                    trigtime = '20'+grb_name[:2]+'-'+grb_name[2:4]+'-'+grb_name[-2:]+'T'+trigtime

            else:
                trigtime = "no_tt"

    # Lone SN cases
    elif 'SN' in event_id or 'AT' in event_id:
        sn_name = event_id[2:]

        # Table with triggertimes
        trigtable = conn.execute(
            'SELECT trigtime FROM TrigCoords WHERE sn_name=?', (sn_name,))

        # Extract the value from the cursor object
        for i in trigtable:
            if i[0] is not None:
                trigtime = i[0]
            else:
                trigtime = "no_tt"
    conn.close()
    # print(trigtime)
    return trigtime

# Dictionary to convert months to numbers
month2number = {'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04', 'May':'05', \
'Jun':'06', 'Jul':'07', 'Aug':'08', 'Sep':'09', 'Oct':'10', 'Nov':'11', \
'Dec':'12', 'January':'01', 'February':'02', 'March':'03', 'April':'04',\
 'June':'06', 'July':'07', 'August':'08', 'September':'09', 'October':'10',\
  'November':'11', 'December':'12'}

def deciday(date):
    """
    A function to turn decimal days into days, hours, minutes and seconds
    """
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

def decihour(decimalhour):
    """
    A function to turn decimal hours into hours, minutes and seconds
    """
    # The hour is everything before the .
    l = float(decimalhour)
    hour =  int(l)
    minute = np.floor(((l-hour)*60) % 60)
    second = ((l-hour)*3600) % 60

    # Make sure the days will match isotime format 2020-02-03T18:14:24 2004-11-02T07:11:59
    if hour<10:
        hour = '0'+str(hour)
    if minute<10:
        minute = '0'+str(minute)
    if second<10:
        second = '0'+str(second)
    return(hour, minute, second)

def elapsed_time(dataframe, trigtime):
    """
    A function to parse date info. This will convert the date data to elapsed time since trigger.
    """
    # Handle the different date formats
    time = []


    for i in range(len(dataframe['date'])):
        # yyyy-month-deciday
        if dataframe['date_unit'][i] == "yyyy-month-deciday":

            # Split the date.
            date = dataframe['date'][i].split('-')
            year = date[0]
            month = month2number[date[1]]

            # Get the deciday to days, hours, min, sec
            day, hour, minute, second = deciday(date[2])

            # Turn into isotime
            isotime = str(year)+'-'+str(month)+'-'+str(day)+'T'+str(hour)+\
            ':'+str(minute)[:2]+':'+str(second)[:2]

            # Handle an absence of triggertime. Set to the first time in the observations.
            if trigtime == 'no_tt' and i==0:
                trigtime = isotime
            # astropy to subtract the two isotimes
            time_list = [isotime, trigtime]
            t = Time(time_list, format='isot', scale='utc')
            time.append(float(t[0])-float(t[1]))

            # Time unit is now in days
            dataframe['time_unit'] = 'days'

        # yyyy-mm-deciday
        elif dataframe['date_unit'][i] == "yyyy-mm-deciday":

            # Split up the date.
            date = dataframe['date'][i].split('-')
            year = date[0]
            month = date[1]

            # Get the deciday to days, hours, min, sec
            day, hour, minute, second = deciday(date[2])

            # Turn into isotime.
            isotime = str(year)+'-'+str(month)+'-'+str(day)+'T'+str(hour)+':'+\
            str(minute)[:2]+':'+str(second)[:2]

            # Handle an absence of triggertime. Set to the first time in the observations.
            if trigtime == 'no_tt' and i==0:
                trigtime = isotime
            # astropy to subtract the two isotimes
            time_list = [isotime, trigtime]
            t = Time(time_list, format='isot', scale='utc')
            time.append(t[0]-t[1])

            # Time unit is now in days
            dataframe['time_unit'] = 'days'

        # yyyy-mm-deciday-deciday
        elif dataframe['date_unit'][i] == "yyyy-mm-deciday-deciday":

            # Split up the date.
            date = dataframe['date'][i].split('-')
            year = date[0]
            month = date[1]

            # Get the deciday to days, hours, min, sec
            day1, hour1, minute1, second1 = deciday(date[2])
            day2, hour2, minute2, second2 = deciday(date[3])

            # Turn into isotime
            isotime1 = str(year)+'-'+str(month)+'-'+str(day1)+'T'+str(hour1)+\
            ':'+str(minute1)[:2]+':'+str(second1)[:2]
            isotime2 = str(year)+'-'+str(month)+'-'+str(day2)+'T'+str(hour2)+\
            ':'+str(minute2)[:2]+':'+str(second2)[:2]

            # Handle an absence of triggertime. Set to the first time in the observations.
            if trigtime == 'no_tt' and i==0:
                trigtime = isotime1

            # astropy to subtract the two isotimes
            time_list = [isotime1, isotime2, trigtime]
            t = Time(time_list, format='isot', scale='utc')
            isotime = t[0]+((t[1]-t[0])/2)
            time.append(isotime-t[2])

            # Time unit is now in days
            dataframe['time_unit'] = 'days'

        # yyyy-month-deciday-deciday
        elif dataframe['date_unit'][i] == "yyyy-month-deciday-deciday":

            # Split up the date.
            date = dataframe['date'][i].split('-')
            year = date[0]
            month = month2number[date[1]]

            # Get the deciday to days, hours, min, sec.
            day1, hour1, minute1, second1 = deciday(date[2])
            day2, hour2, minute2, second2 = deciday(date[3])

            # Turn into isotime
            isotime1 = str(year)+'-'+str(month)+'-'+str(day1)+'T'+str(hour1)+\
            ':'+str(minute1)[:2]+':'+str(second1)[:2]
            isotime2 = str(year)+'-'+str(month)+'-'+str(day2)+'T'+str(hour2)+\
            ':'+str(minute2)[:2]+':'+str(second2)[:2]

            # Handle an absence of triggertime. Set to the first time in the observations.
            if trigtime == 'no_tt' and i==0:
                trigtime = isotime1

            # astropy to subtract the two isotimes.
            time_list = [isotime1, isotime2, trigtime]
            t = Time(time_list, format='isot', scale='utc')
            isotime = t[0]+((t[1]-t[0])/2)
            time.append(isotime-t[2])

            # Time unit is now in days
            dataframe['time_unit'] = 'days'

        # yyyy-mm-dd-hh:mm-hh:mm
        elif dataframe['date_unit'][i] == "yyyy-mm-dd-hh:mm-hh:mm":
            # Split up the date.
            date = dataframe['date'][i].split('-')
            year = date[0]
            month = date[1]
            day = date[2]

            # hours, minutes, seconds
            a = str(date[3]).split(":")
            hour1 = a[0]
            minute1 =  a[1]

            b = str(date[4]).split(":")
            hour2 = b[0]
            minute2 =  b[1]

            # Turn into isotime.
            isotime1 = str(year)+'-'+str(month)+'-'+str(day)+'T'+\
            str(hour1)+':'+str(minute1)[:2]+':00'
            isotime2 = str(year)+'-'+str(month)+'-'+str(day)+'T'+\
            str(hour2)+':'+str(minute2)[:2]+':00'

            # Handle an absence of triggertime. Set to the first time in the observations.
            if trigtime == 'no_tt' and i==0:
                trigtime = isotime1

            # astropy to subtract the two isotimes and get the median time.
            time_list = [isotime1, isotime2, trigtime]
            t = Time(time_list, format='isot', scale='utc')
            isotime = t[0]+((t[1]-t[0])/2)
            time.append(isotime-t[2])

            # Time unit is now in days.
            dataframe['time_unit'] = 'days'

        # yyyy-month-dd-hh:mm-hh:mm
        elif dataframe['date_unit'][i] == "yyyy-month-dd-hh:mm-hh:mm":
            # Split up the date.
            date = dataframe['date'][i].split('-')
            year = date[0]
            month = month2number[date[1]]
            day = date[2]

            # hours, minutes, seconds
            a = str(date[3]).split(":")
            hour1 = a[0]
            minute1 =  a[1]

            b = str(date[4]).split(":")
            hour2 = b[0]
            minute2 =  b[1]

            # Turn into isotime
            isotime1 = str(year)+'-'+str(month)+'-'+str(day)+'T'+str(hour1)+\
            ':'+str(minute1)[:2]+':00'
            isotime2 = str(year)+'-'+str(month)+'-'+str(day)+'T'+str(hour2)+\
            ':'+str(minute2)[:2]+':00'

            # Handle an absence of triggertime. Set to the first time in the observations.
            if trigtime == 'no_tt' and i==0:
                trigtime = isotime1

            # astropy to subtract the two isotimes and get the median time.
            time_list = [isotime1, isotime2, trigtime]
            t = Time(time_list, format='isot', scale='utc')
            isotime = t[0]+((t[1]-t[0])/2)
            time.append(isotime-t[2])

            # Time unit is now in days.
            dataframe['time_unit'] = 'days'

        # MJD
        elif dataframe['date_unit'][i] == "MJD":
            print(file, ' used MJD')
            # Split the two MJDs.
            mjd = dataframe['date'][i]

            # Convert the MJDs to isotimes.
            mjdiso = Time(mjd, format='mjd')
            obstime = Time(mjdiso.isot, format='isot')

            # Handle an absence of triggertime. Set to the first time in the observations.
            if trigtime == 'no_tt' and i==0:
                trigtime = obstime

            # Append the isotime-trigtime (elapsed time)
            time.append(obstime-Time(trigtime, format='isot'))

            # Time unit is now in days
            dataframe['time_unit'] = 'days'

        # yyyy-month-day-hh:mm
        elif dataframe['date_unit'][i] == 'yyyy-month-day-hh:mm':
            date = dataframe['date'][i].split('-')
            year = date[0]
            month = date[1]
            day = date[2]

            # hours, minutes
            a = str(date[3]).split(":")
            hour1 = a[0]
            minute1 =  a[1]

            # Turn into isotime
            isotime1 = str(year)+'-'+str(month2number[month])+'-'+str(day)+\
            'T'+str(hour1)+':'+str(minute1)[:2]+':00'

            # Handle an absence of triggertime. Set to the first time in the observations.
            if trigtime == 'no_tt' and i==0:
                trigtime = isotime1

            # astropy to subtract the two isotimes and get the elapsed time
            time_list = [isotime1, trigtime]
            t = Time(time_list, format='isot', scale='utc')
            time.append(t[0]-t[1])

            # Time unit is now in days
            dataframe['time_unit'] = 'days'


        # MJD-MJD
        elif dataframe['date_unit'][i] == 'MJD-MJD':

            # Split the two MJDs
            mjds = dataframe['date'][i].split('-')

            mjd1 = mjds[0]
            mjd2 = mjds[1]

            # Convert the MJDs to isotimes.
            mjd1iso = Time(mjd1, format='mjd')
            mjd1iso = Time(mjd1iso.isot, format='isot')
            mjd2iso = Time(mjd2, format='mjd')
            mjd2iso = Time(mjd2iso.isot, format='isot')

            # Work out the central time.
            obstime = mjd1iso+((mjd2iso-mjd1iso)/2)

            # Handle an absence of triggertime. Set to the first time in the observations.
            # print(trigtime)
            if trigtime == 'no_tt' and i==0:
                trigtime = obstime

            # Append the isotime-trigtime (elapsed time)
            time.append(obstime-Time(trigtime, format='isot'))

            # Time unit is now in days
            dataframe['time_unit'] = 'days'

        # yyyy-month-deciday-month-deciday
        # This could have issues if only the date is given.
        elif dataframe['date_unit'][i] == 'yyyy-month-deciday-month-deciday':

            # Split the date up.
            date = dataframe['date'][i].split('-')

            # Write out the dates as isotimes.
            year = date[0]
            month1 = month2number[date[1]]
            month2 = month2number[date[3]]

            # Get the deciday to days, hours, min, sec
            day1, hour1, minute1, second1 = deciday(date[2])
            day2, hour2, minute2, second2 = deciday(date[4])

            # Turn into isotime
            isotime1 = str(year)+'-'+str(month1)+'-'+str(day1)+'T'+\
            str(hour1)+':'+str(minute1)[:2]+':'+str(second1)[:2]
            isotime2 = str(year)+'-'+str(month2)+'-'+str(day2)+'T'+\
            str(hour2)+':'+str(minute2)[:2]+':'+str(second2)[:2]

            # Work out the time in the middle of the two isotimes.
            time_list = [isotime1, isotime2]
            t = Time(time_list, format='isot', scale='utc')
            obstime = t[0]+((t[1]-t[0])/2)

            # Handle an absence of triggertime. Set to the first time in the observations.
            if trigtime == 'no_tt' and i==0:
                trigtime = obstime

            # Append the isotime-trigtime (elapsed time)
            time.append(obstime-Time(trigtime, format='isot', scale='utc'))

            # Time unit is now in days
            dataframe['time_unit'] = 'days'

        # yyyy-month-dd-hh.h-hh.h
        elif dataframe['date_unit'][i] == 'yyyy-month-dd-hh.h-hh.h':

            # Split the date up.
            date = dataframe['date'][i].split('-')

            # Write out the dates as isotimes.
            year = date[0]
            month = month2number[date[1]]
            day = date[2]

            # Get the decimal hours into hours, minutes, seconds.
            hour1, minute1, second1 = decihour(date[3])
            hour2, minute2, second2 = decihour(date[4])

            # Turn into isotime
            isotime1 = str(year)+'-'+str(month)+'-'+str(day)+'T'+str(hour1)+\
            ':'+str(minute1)[:2]+':'+str(second1)[:2]
            isotime2 = str(year)+'-'+str(month)+'-'+str(day)+'T'+str(hour2)+\
            ':'+str(minute2)[:2]+':'+str(second2)[:2]

            # Work out the time in the middle of the two isotimes.
            time_list = [isotime1, isotime2]
            t = Time(time_list, format='isot', scale='utc')
            obstime = t[0]+((t[1]-t[0])/2)

            # Handle an absence of triggertime. Set to the first time in the observations.
            if trigtime == 'no_tt' and i==0:
                trigtime = obstime

            # Append the isotime-trigtime (elapsed time)
            time.append(obstime-Time(trigtime, format='isot', scale='utc'))

            # Time unit is now in days
            dataframe['time_unit'] = 'days'

        # Alert me that I have encountered a date format that isn't supported yet.
        else:
            raise Exception('No date2time function found for '+\
                dataframe['date_unit'][i]+' , time to write a new \
                function for converting dates to times.')

    # update the time column with the new times.
    dataframe['time'] = time

    return dataframe

def delta_time(dataframe):
    """
    Calculates the delta value when the times/dates are ranges.
    """

    # Create the dtime array, fill with NaN.
    dtime = np.empty(len(dataframe[list(dataframe.keys())[0]]))
    dtime[:] = np.NaN

    if 'date' in list(dataframe.keys()):
        for i in range(len(dataframe['date'])):

            # yyyy-mm-deciday-deciday
            if dataframe['date_unit'][i] == "yyyy-mm-deciday-deciday":

                # Split up the date.
                date = dataframe['date'][i].split('-')
                year = date[0]
                month = date[1]

                # Get the deciday to days, hours, min, sec
                day1, hour1, minute1, second1 = deciday(date[2])
                day2, hour2, minute2, second2 = deciday(date[3])

                # Turn into isotime
                isotime1 = str(year)+'-'+str(month)+'-'+str(day1)+'T'+str(hour1)+\
                ':'+str(minute1)[:2]+':'+str(second1)[:2]
                isotime2 = str(year)+'-'+str(month)+'-'+str(day2)+'T'+str(hour2)+\
                ':'+str(minute2)[:2]+':'+str(second2)[:2]

                # astropy to subtract the two isotimes
                time_list = [isotime1, isotime2]
                t = Time(time_list, format='isot', scale='utc')

                # This one has a range of times. Add the error on the range to the dtime array.
                delta_time = ((t[1]-t[0])/2)
                dtime[i] = (delta_time.to_value(format='sec', subfmt='decimal'))/86400

                # Time unit is now in days
                dataframe['time_unit'] = 'days'

            # yyyy-month-deciday-deciday
            elif dataframe['date_unit'][i] == "yyyy-month-deciday-deciday":

                # Split up the date.
                date = dataframe['date'][i].split('-')
                year = date[0]
                month = month2number[date[1]]

                # Get the deciday to days, hours, min, sec.
                day1, hour1, minute1, second1 = deciday(date[2])
                day2, hour2, minute2, second2 = deciday(date[3])

                # Turn into isotime
                isotime1 = str(year)+'-'+str(month)+'-'+str(day1)+'T'+str(hour1)+\
                ':'+str(minute1)[:2]+':'+str(second1)[:2]
                isotime2 = str(year)+'-'+str(month)+'-'+str(day2)+'T'+str(hour2)+\
                ':'+str(minute2)[:2]+':'+str(second2)[:2]

                # astropy to subtract the two isotimes.
                time_list = [isotime1, isotime2]
                t = Time(time_list, format='isot', scale='utc')

                # This one has a range of times. Add the error on the range to the dtime array.
                delta_time = ((t[1]-t[0])/2)
                dtime[i] = (delta_time.to_value(format='sec', subfmt='decimal'))/86400

                # Time unit is now in days
                dataframe['time_unit'] = 'days'


            # yyyy-mm-dd-hh:mm-hh:mm
            elif dataframe['date_unit'][i] == "yyyy-mm-dd-hh:mm-hh:mm":
                # Split up the date.
                date = dataframe['date'][i].split('-')
                year = date[0]
                month = date[1]
                day = date[2]

                # hours, minutes, seconds
                a = str(date[3]).split(":")
                hour1 = a[0]
                minute1 =  a[1]

                b = str(date[4]).split(":")
                hour2 = b[0]
                minute2 =  b[1]

                # Turn into isotime
                isotime1 = str(year)+'-'+str(month)+'-'+str(day)+'T'+str(hour1)+\
                ':'+str(minute1)[:2]+':00'
                isotime2 = str(year)+'-'+str(month)+'-'+str(day)+'T'+str(hour2)+\
                ':'+str(minute2)[:2]+':00'

                # astropy to subtract the two isotimes and get the median time.
                time_list = [isotime1, isotime2]
                t = Time(time_list, format='isot', scale='utc')

                # This one has a range of times. Add the error on the range to the dtime array.
                delta_time = ((t[1]-t[0])/2)
                dtime[i] = (delta_time.to_value(format='sec', subfmt='decimal'))/86400

                # Time unit is now in days
                dataframe['time_unit'] = 'days'

            # yyyy-month-dd-hh:mm-hh:mm
            elif dataframe['date_unit'][i] == "yyyy-month-dd-hh:mm-hh:mm":
                # Split up the date.
                date = dataframe['date'][i].split('-')
                year = date[0]
                month = month2number[date[1]]
                day = date[2]

                # hours, minutes, seconds
                a = str(date[3]).split(":")
                hour1 = a[0]
                minute1 =  a[1]

                b = str(date[4]).split(":")
                hour2 = b[0]
                minute2 =  b[1]

                # Turn into isotime
                isotime1 = str(year)+'-'+str(month)+'-'+str(day)+'T'+str(hour1)+\
                ':'+str(minute1)[:2]+':00'
                isotime2 = str(year)+'-'+str(month)+'-'+str(day)+'T'+str(hour2)+\
                ':'+str(minute2)[:2]+':00'

                # astropy to subtract the two isotimes and get the median time.
                time_list = [isotime1, isotime2]
                t = Time(time_list, format='isot', scale='utc')

                # This one has a range of times. Add the error on the range to the dtime array.
                delta_time = ((t[1]-t[0])/2)
                dtime[i] = (delta_time.to_value(format='sec', subfmt='decimal'))/86400

                # Time unit is now in days
                dataframe['time_unit'] = 'days'

            # MJD-MJD
            elif dataframe['date_unit'][i] == 'MJD-MJD':

                # Split the two MJDs
                mjds = dataframe['date'][i].split('-')

                mjd1 = mjds[0]
                mjd2 = mjds[1]

                # Convert the MJDs to isotimes.
                mjd1iso = Time(mjd1, format='mjd')
                mjd1iso = Time(mjd1iso.isot, format='isot')
                mjd2iso = Time(mjd2, format='mjd')
                mjd2iso = Time(mjd2iso.isot, format='isot')

                # This one has a range of times. Add the error on the range to the dtime array.
                delta_time = ((mjd2iso-mjd1iso)/2)
                dtime[i] = (delta_time.to_value(format='sec', subfmt='decimal'))/86400

                # Time unit is now in days
                dataframe['time_unit'] = 'days'

            # yyyy-month-deciday-month-deciday
            # Note that this could have issues if only the date is given.
            elif dataframe['date_unit'][i] == 'yyyy-month-deciday-month-deciday':

                # Split the date up.
                date = dataframe['date'][i].split('-')

                # Write out the dates as isotimes.
                year = date[0]
                month1 = month2number[date[1]]
                month2 = month2number[date[3]]

                # Get the deciday to days, hours, min, sec
                day1, hour1, minute1, second1 = deciday(date[2])
                day2, hour2, minute2, second2 = deciday(date[4])

                # Turn into isotime
                isotime1 = str(year)+'-'+str(month1)+'-'+str(day1)+'T'+str(hour1)+':'+\
                str(minute1)[:2]+':'+str(second1)[:2]
                isotime2 = str(year)+'-'+str(month2)+'-'+str(day2)+'T'+str(hour2)+':'+\
                str(minute2)[:2]+':'+str(second2)[:2]

                # Work out the time in the middle of the two isotimes.
                time_list = [isotime1, isotime2]
                t = Time(time_list, format='isot', scale='utc')

                # This one has a range of times. Add the error on the range to the dtime array.
                delta_time = ((t[1]-t[0])/2)
                dtime[i] = (delta_time.to_value(format='sec', subfmt='decimal'))/86400

                # Time unit is now in days
                dataframe['time_unit'] = 'days'

            # yyyy-month-dd-hh.h-hh.h
            elif dataframe['date_unit'][i] == 'yyyy-month-dd-hh.h-hh.h':

                # Split the date up.
                date = dataframe['date'][i].split('-')

                # Write out the dates as isotimes.
                year = date[0]
                month = month2number[date[1]]
                day = date[2]

                # Get the decimal hours into hours, minutes, seconds.
                hour1, minute1, second1 = decihour(date[3])
                hour2, minute2, second2 = decihour(date[4])

                # Turn into isotime
                isotime1 = str(year)+'-'+str(month)+'-'+str(day)+'T'+str(hour1)+':'+\
                str(minute1)[:2]+':'+str(second1)[:2]
                isotime2 = str(year)+'-'+str(month)+'-'+str(day)+'T'+str(hour2)+':'+\
                str(minute2)[:2]+':'+str(second2)[:2]

                # Work out the time in the middle of the two isotimes.
                time_list = [isotime1, isotime2]
                t = Time(time_list, format='isot', scale='utc')

                # This one has a range of times. Add the error on the range to the dtime array.
                delta_time = ((t[1]-t[0])/2)
                dtime[i] = (delta_time.to_value(format='sec', subfmt='decimal'))/86400

                # Time unit is now in days
                dataframe['time_unit'] = 'days'
        dataframe['dtime'] = dtime

    # The dtime should just be nan.
    else:
        dataframe['dtime'] = dtime

    return dataframe

def time_formats(dataframe):
    """
    This function will handle any days-days, seconds-seconds and
    minutes-minutes in the time columns.
    """
    # Create a dtime column if these exist in the time column. Initially fill it with zeros.
    check = 0
    if 'dtime' not in list(dataframe.keys()):
        dtime = np.zeros(len(dataframe['time_unit']))

    # Handle the different date formats
    for i in range(len(dataframe['time'])):

        # seconds-seconds
        if dataframe['time_unit'][i] == "seconds-seconds":
            check = 1
            # Initial time and second time.
            t1 = float(str(dataframe['time'][i]).split('-', maxsplit=1)[0])
            t2 = float(str(dataframe['time'][i]).split('-')[1])
            dataframe['time'][i] = t1+(t2-t1)/2
            dtime[i] = (t2-t1)/2
            dataframe['time_unit'][i] = 'seconds'

        # minutes-minutes
        if dataframe['time_unit'][i] == "minutes-minutes":
            check = 1
            # Initial time and second time.
            t1 = float(str(dataframe['time'][i]).split('-', maxsplit=1)[0])
            t2 = float(str(dataframe['time'][i]).split('-')[1])
            dataframe['time'][i] = t1+(t2-t1)/2
            dtime[i] = (t2-t1)/2
            dataframe['time_unit'][i] = 'minutes'

        # hours-hours
        if dataframe['time_unit'][i] == "hours-hours":
            check = 1
            # Initial time and second time.
            t1 = float(str(dataframe['time'][i]).split('-', maxsplit=1)[0])
            t2 = float(str(dataframe['time'][i]).split('-')[1])
            dataframe['time'][i] = t1+(t2-t1)/2
            dtime[i] = (t2-t1)/2
            dataframe['time_unit'][i] = 'hours'

        # days-days
        if dataframe['time_unit'][i] == "days-days":
            check = 1
            # Initial time and second time.
            t1 = float(str(dataframe['time'][i]).split('-', maxsplit=1)[0])
            t2 = float(str(dataframe['time'][i]).split('-')[1])
            dataframe['time'][i] = t1+(t2-t1)/2
            dtime[i] = (t2-t1)/2
            dataframe['time_unit'][i] = 'days'

    # If there was a need to make the dtime column then make a dtime column.
    if check==1:
        dataframe['dtime'] = dtime

    return dataframe

# Filename keywords
# Possible wavelengths in the filenames.
wavelength_names = ['xray', 'uv', 'optical', 'nir', 'ir', 'radio']
# Possible optical data tags in filenames.
optical_filetags = ['optical', 'nir', 'uv', 'ir']
# Possible tags in the radio filenames.
radio_filetags = ['radio']
# Possible tags in the xray filenames.
xray_filetags = ['xray']

def limits(df, wave_range):
    """
    This function will create a column with a value that tells us
    whether the magnitude/flux_density etc is an upper/lower limit
    or just a normal value.
    """
    # Radio files
    if any(substring in wave_range.lower() for substring in radio_filetags):
        if 'flux_density' in list(df.keys()):
            i = 'flux_density'

        if 'flux' in list(df.keys()):
            i = 'flux'

    # Optical files
    if any(substring in wave_range.lower() for substring in optical_filetags):
        i = 'mag'

    # Xray files
    if any(substring in wave_range.lower() for substring in xray_filetags):
        i = 'flux'

    # Convert the column to string
    df[i] = df[i].astype(str)


    # Upper limit = 1, Lower limit = -1, Neither = 0
    conditions = [(df[i].str.contains('>')), (df[i].str.contains('<'))]
    choices = [-1, 1]
    df.insert(df.columns.get_loc(i)+1, i+str('_limit'), np.select(conditions, choices, default=0))

    # Replace any < or > there may be
    df[i] = df[i].str.replace('<', '')
    df[i] = df[i].str.replace('>', '')

    # Convert back to float
    df[i] = df[i].astype(float)

    return df

def nondetections(df, wave_range):
    '''
    Checks if there is a NaN in the flux_density or mag columns.
    If there is then it checks if there is data in the dflux_density/dmag column.
    If there is it puts this data into the flux_density/mag column and
    places a NaN in dflux_density/dmag column.
    If both are NaN then it sets the flux_density_limit/mag_limit column to 2.
    This can then be filtered out in the app.py function.
    '''

    # Radio files
    if any(substring in wave_range.lower() for substring in radio_filetags):
        if 'flux_density' in list(df.keys()):
            i = 'flux_density'
            j = 'dflux_density'
            k = 'flux_density_limit'

        elif 'flux' in list(df.keys()):
            i = 'flux'
            j = 'dflux'
            k = 'flux_limit'

    # Optical files
    if any(substring in wave_range.lower() for substring in optical_filetags):
        i = 'mag'
        j = 'dmag'
        k = 'mag_limit'

    # Xray files
    if any(substring in wave_range.lower() for substring in xray_filetags):
        i = 'flux'
        j = 'dflux'
        k = 'flux_limit'

    # Get the rows where the flux/mag is NaN, set them to the value of the error rows.
    df2 = df.iloc[df[df[i].isnull()].index.tolist()]

    if df2.empty is False:
        # Indices where the mag/fd is nan
        index_list = df[df[i].isnull()].index.tolist()
        # Indices where the dmag/dfd is nan and themag/fd is nan in the new df.
        index_list2 = df2[df2[j].isnull()].index.tolist()

        index_list3 = []
        for m in index_list:
            if m not in index_list2:
                # All the indices where there are null mag/fd but that have a dmag/dfd.
                index_list3.append(m)

        # Set the mag/fd to the error value.
        df.iloc[index_list3, df.columns.get_loc(i)] = df.iloc[index_list3, df.columns.get_loc(j)]

        # Update the limit column so that it is 1 (upper limit)
        df.iloc[index_list3, df.columns.get_loc(k)] = 1

        # Set the error rows to NaN.
        df.iloc[index_list3, df.columns.get_loc(j)] = 'NaN'

    return df

def masterfileformat(event):
    '''
    Iterate over any txt files with data for a GRB in a specific wavelength range.
    Put them all together with an outer join on their pandas.
    Save to a csv called GRBXXXXXX-SNXXXXxx_waverange_Master.txt
    '''

    optical_pandas = []
    radio_pandas = []
    xray_pandas = []

    # Get the file sources for each data file of the GRB
    file_sources = pd.read_csv(event+'filesources.csv', header=0, sep=',')

    for file in file_list:
        print(file)
        if 'Master' in file:
            continue
        # Radio master db
        if any(substring in file.lower() for substring in radio_filetags):
            data = pd.read_csv(file, sep='\t')

            # Add a column for the ads abstract link - source.
            # This comes out of the filesources.csv file.
            data['reference'] = len(data['time'])*[file_sources.at\
            [file_sources[file_sources['Filename']==\
            file].index[0], 'Reference']]

            # Make sure the elapsed time is in days,
            # if its in seconds/minutes/hours then convert it.
            time = np.array(data['time'], dtype=np.float64)
            for i in range(len(data['time_unit'])):
                if data['time_unit'][i] == 'seconds':
                    time[i] = float(time[i])/86400

                elif data['time_unit'][i] == 'minutes':
                    time[i] = float(time[i])/1440

                elif data['time_unit'][i] == 'hours':
                    time[i] = float(time[i])/24

            data['time'] = time
            data['time_unit'] = 'days'

            # Append pandas
            radio_pandas.append(data)

        # Optical master db
        elif any(substring in file.lower() for substring in optical_filetags):
            data = pd.read_csv(file, sep='\t')

            # Add a column for the ads abstract link - source
            data['reference'] = len(data['time'])*[file_sources.at\
            [file_sources[file_sources['Filename']==\
            file].index[0], 'Reference']]

            # Make sure the elapsed time is in days,
            # if its in seconds/minutes/hours then convert it.
            time = np.array(data['time'], dtype=np.float64)
            for i in range(len(data['time_unit'])):
                if data['time_unit'][i] == 'seconds':
                    time[i] = float(time[i])/86400

                elif data['time_unit'][i] == 'minutes':
                    time[i] = float(time[i])/1440

                elif data['time_unit'][i] == 'hours':
                    time[i] = float(time[i])/24

            data['time'] = time
            data['time_unit'] = 'days'

            # Append pandas
            optical_pandas.append(data)

        # Xray files
        elif any(substring in file.lower() for substring in xray_filetags):
            data = pd.read_csv(file, sep='\t')

            # Add a column for the ads abstract link - source
            data['reference'] = len(data['time'])*[file_sources.at\
            [file_sources[file_sources['Filename']==\
            file].index[0], 'Reference']]

            # Make sure the elapsed time is in seconds,
            # if its in days/minutes/hours then convert it.
            time = np.array(data['time'], dtype=np.float64)
            for i in range(len(data['time_unit'])):
                if data['time_unit'][i] == 'days':
                    time[i] = float(time[i])*86400

                elif data['time_unit'][i] == 'minutes':
                    time[i] = float(time[i])*60

                elif data['time_unit'][i] == 'hours':
                    time[i] = float(time[i])*3600

            data['time'] = time
            data['time_unit'] = 'seconds'

            # Append pandas
            xray_pandas.append(data)

    # Create the master files.
    if len(radio_pandas) != 0:
        radio = pd.concat(radio_pandas, join='outer')
        radio.to_csv(event+'_Radio_Master.txt', sep='\t', index=False, na_rep='NaN')

    if len(optical_pandas) != 0:
        optical = pd.concat(optical_pandas, join='outer')
        optical.to_csv(event+'_Optical_Master.txt', sep='\t', index=False, na_rep='NaN')

    if len(xray_pandas) != 0:
        xray = pd.concat(xray_pandas, join='outer')
        xray.to_csv(event+'_Xray_Master.txt', sep='\t', index=False, na_rep='NaN')

###################
#### MAIN #########
###################
# Run through all the files. Convert them to the format we want.
for i in range(len(event_list)):
    # print('I am now doing folder: ', event_list[i])
    trigtime = get_trigtime(event_list[i])

    os.chdir("SourceData/")
    os.chdir(event_list[i])

    file_list = glob.glob("*.txt")

    # Check if the readme exists already. If it does then the files are ready to parse.
    if 'readme.txt' in file_list:
        for file in file_list:
            if 'Master' in file:
                print('Skipping ', file)
                continue

            # Radio files
            if any(substring in file.lower() for substring in radio_filetags):

                data = pd.read_csv(file, sep='\t')

                # Find and catalogue limit values
                if 'flux_density_limit' not in list(data.keys()) and \
                'flux_limit' not in list(data.keys()):
                    data = limits(data, file)

                # Tag any non-detections.
                data = nondetections(data, file)

                # Calculate the elapsed time
                if 'time' not in list(data.keys()):
                    data = elapsed_time(data, trigtime)
                if 'dtime' not in list(data.keys()):
                    data = delta_time(data)

                time_formats(data)

                data.to_csv(file, sep='\t', index=False, na_rep='NaN')

            # Optical files
            elif any(substring in file.lower() for substring in optical_filetags):

                data = pd.read_csv(file, sep='\t')

                # Find and catalogue limit values
                if 'mag_limit' not in list(data.keys()):
                    data = limits(data, file)

                # Tag any non-detections.
                data = nondetections(data, file)

                # Calculate the elapsed time
                if 'time' not in list(data.keys()):
                    data = elapsed_time(data, trigtime)
                if 'dtime' not in list(data.keys()):
                    data = delta_time(data)

                time_formats(data)

                data.to_csv(file, sep='\t', index=False, na_rep='NaN')

            # Xray files
            elif any(substring in file.lower() for substring in xray_filetags):

                data = pd.read_csv(file, sep='\t')

                # Find and catalogue limit values
                if 'flux_limit' not in list(data.keys()):
                    data = limits(data, file)

                # Tag any non-detections.
                data = nondetections(data, file)

                # Calculate the elapsed time
                if 'time' not in list(data.keys()):
                    data = elapsed_time(data, trigtime)
                if 'dtime' not in list(data.keys()):
                    data = delta_time(data)

                time_formats(data)

                data.to_csv(file, sep='\t', index=False, na_rep='NaN')

            # Don't go over the readmes or other data.
            else:
                print('Skipping: ', file)

        # Convert all the files to one master file for Optical/NIR.
        masterfileformat(event_list[i])

    os.chdir('..')
    os.chdir('..')
