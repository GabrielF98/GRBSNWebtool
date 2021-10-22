import numpy as np
import pandas as pd

#Add the bit for the database access:
import sqlite3
def get_db_connection():
    conn = sqlite3.connect('Masterbase.db')
    conn.row_factory = sqlite3.Row
    return conn

#Get the data from the text file
data = pd.read_csv('RA_Dec_Data_SwiftGRBs/GRBBulkParamsfromtheswiftWebsite.txt', sep='\t')

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

print(grbs)

#Loop over the grb names and then cross reference them with the panda to get an RA and Dec
grb_names_txtfile = np.array(data['GRB'])
ra_txtfile = np.array(data['BAT RA (J2000)'])
dec_txtfile = np.array(data['BAT Dec (J2000)'])

ra = np.zeros(len(grbs))
dec = np.zeros(len(grbs))

for i in range(len(grbs)):
	for j in range(len(grb_names_txtfile)):
		if grbs[i]==grb_names_txtfile[j]:
			ra[i] = ra_txtfile[i]
			dec[i] = dec_txtfile[i]


for i in range(len(grbs)):
	print(grbs[i], ra[i], dec[i])


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
                                        source text
                                    ); """

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_radec_table)

    else:
        print("Error! cannot create the database connection.")


#Add the data
# sqliteConnection = sqlite3.connect('Masterbase.db')
# cursor = sqliteConnection.cursor()

# for i in range(len(grbs)):
# 	query = ('INSERT INTO RADec (grb_id, ra, dec, source) VALUES (?, ?, ?, ?)')
# 	count = cursor.execute(query, (grbs[i], ra[i], dec[i], "https://swift.gsfc.nasa.gov/archive/grb_table/"))
# 	sqliteConnection.commit()

# cursor.close()

if __name__ == '__main__':
    main()

