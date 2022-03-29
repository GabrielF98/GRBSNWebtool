import numpy as np
import pandas as pd

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
    names = conn.execute('SELECT DISTINCT(GRB) FROM SQLDataGRBSNe WHERE GRB IS NOT NULL')
    grbs = []
    for i in names:
    	grbs.append(i[0])
    conn.close()
    
    return grbs
grbs = grb_names()

#print(grbs)

#Loop over the grb names and then cross reference them with the panda to get an RA and Dec

from astropy import units as u
from astropy.coordinates import SkyCoord

grb_names_txtfile = np.array(data['GRB'])
ra_txtfile = np.array(data['XRT RA (J2000)'])
dec_txtfile = np.array(data['XRT Dec (J2000)'])
triggers = np.array(data['Time [UT]'])

ra = np.zeros((len(grbs)))
dec = np.zeros((len(grbs)))
trig_time = np.zeros(len(grbs))

for i in range(len(grbs)):
    for j in range(len(grb_names_txtfile)):
        if grbs[i]==grb_names_txtfile[j] and str(ra_txtfile[j])!='nan' and str(dec_txtfile[j])!='nan':
            print("The values are:", ra_txtfile[j], dec_txtfile[j])
            ra_components = ra_txtfile[j].split(':')
            dec_components = dec_txtfile[j].split(':')
            print(grbs[i])
            print(ra_components, dec_components)
            ra_string = str(ra_components[0])+'h'+str(ra_components[1])+'m'+str(ra_components[2])+'s'
            dec_string = str(dec_components[0])+'d'+str(dec_components[1])+'m'+str(dec_components[2])+'s'
            print(ra_string, dec_string)

            c = SkyCoord(ra_string, dec_string)
            ra[i] = round(float(c.ra.value), 3)
            dec[i] = round(float(c.dec.value), 3)
            
            #Add the triggertime
            trig_time[i] = triggers[i]


# for i in range(len(grbs)):
# 	print(grbs[i], ra[i], dec[i])


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

    sql_create_radec_table = """ CREATE TABLE IF NOT EXISTS RADec (
                                        grb_id text,
                                        sn_name text,
                                        ra text,
                                        dec text,
                                        ra_err text,
                                        dec_err text,
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


#Add the data
sqliteConnection = sqlite3.connect('Masterbase.db')
cursor = sqliteConnection.cursor()

for i in range(len(grbs)):
	query = ('INSERT INTO RADec (grb_id, sn_id, trigtime, ra, dec, ra_err, dec_err, source) VALUES (?, ?, ?, ?, ?, ?, ?, ?)')
	count = cursor.execute(query, (grbs[i], None, trig_time[i], ra[i], dec[i], None, None, "https://swift.gsfc.nasa.gov/archive/grb_table/"))
	sqliteConnection.commit()

cursor.close()

if __name__ == '__main__':
    main()

