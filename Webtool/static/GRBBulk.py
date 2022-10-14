'''
Used to create the RADec and trigtimes into the TrigCoords table of the database. 
'''

import numpy as np
import pandas as pd
from astropy import units as u
from astropy.coordinates import SkyCoord

#Add the bit for the database access:
import sqlite3
def get_db_connection():
    conn = sqlite3.connect('Masterbase.db')
    conn.row_factory = sqlite3.Row
    return conn

#Get the data from the text file
data = pd.read_csv('RA_Dec_Data_SwiftGRBs/grb_table_1648223358.txt', sep='\t')

#Get the data on what GRBs we need to look at.
#To do this access the database
def grb_names():
    conn = get_db_connection()
    names = conn.execute('SELECT DISTINCT GRB, SNe FROM SQLDataGRBSNe')
    grbs = []
    sne = []
    for i in names:
        grbs.append(i[0])
        sne.append(i[1])
    conn.close()
    
    return grbs, sne

grbs, sne = grb_names()

#Loop over the grb names and then cross reference them with the panda to get an RA and Dec
grb_names_txtfile = np.array(data['GRB'])
ra_txtfile = np.array(data['XRT RA (J2000)'])
dec_txtfile = np.array(data['XRT Dec (J2000)'])
triggers = np.array(data['Time [UT]'])

ra_decimal = np.zeros((len(grbs)))
dec_decimal = np.zeros((len(grbs)))
ra = []
dec = []
trig_times = []
for k in range(len(grbs)):
    ra.append(None)
    dec.append(None)
    trig_times.append(None)
    ra_decimal[k] = None
    dec_decimal[k] = None

#Loop over the names in our database
for i in range(len(grbs)):
    #Loop over the names in the swift file
    for j in range(len(grb_names_txtfile)):
        #Check that there are non-nan RA and Dec when we match the names
        if grbs[i]==grb_names_txtfile[j]:
            if str(ra_txtfile[j])!='nan'and str(dec_txtfile[j])!='nan':

                #Split the hh:mm:ss formats for conversion
                ra_components = ra_txtfile[j].split(':')
                dec_components = dec_txtfile[j].split(':')

                #Turn into strings for use with astropy
                ra_string = str(ra_components[0])+'h'+str(ra_components[1])+'m'+str(ra_components[2])+'s'
                dec_string = str(dec_components[0])+'d'+str(dec_components[1])+'m'+str(dec_components[2])+'s'

                #Convert to decimal
                c = SkyCoord(ra_string, dec_string)
                ra_decimal[i] = round(float(c.ra.value), 3)
                dec_decimal[i] = round(float(c.dec.value), 3)

                #Save the regular ra and dec also
                ra[i] = ra_txtfile[j]
                dec[i] = dec_txtfile[j]

            #Add the triggertime
            trig_times[i] = triggers[j]


print(ra_decimal)
print(ra)
print(trig_times)

#Making the table in the database
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def main():
    database = r"Masterbase.db"

    sql_create_radec_table = """ CREATE TABLE IF NOT EXISTS TrigCoords (
                                        grb_id text,
                                        sn_name text,
                                        trigtime text,
                                        ra text,
                                        ra_decimal text,
                                        dec text,
                                        dec_decimal text,
                                        ra_deci_err text,
                                        dec_deci_err text,
                                        source text
                                    ); """

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create table
        create_table(conn, sql_create_radec_table)

    else:
        print("Error! cannot create the database connection.")




if __name__ == '__main__':
    # main()
    # #Add the data
    # sqliteConnection = sqlite3.connect('Masterbase.db')
    # cursor = sqliteConnection.cursor()
    # print(len(trig_times), len(grbs))
    # for i in range(len(grbs)):
    #     query = ('INSERT INTO TrigCoords (grb_id, sn_name, trigtime, ra, ra_decimal, dec, dec_decimal, ra_deci_err, dec_deci_err, source)VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)')
    #     count = cursor.execute(query, (grbs[i], sne[i], trig_times[i], ra[i], ra_decimal[i], dec[i], dec_decimal[i], None, None, "https://swift.gsfc.nasa.gov/archive/grb_table/"))
    #     sqliteConnection.commit()

    # cursor.close()
