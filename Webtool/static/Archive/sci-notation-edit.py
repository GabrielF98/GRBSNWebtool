'''
This script can be used to replace capital "E" with "e" in the database. This is needed for python to read the scientific notation correctly. 
'''

import sqlite3

def get_db_connection():
    conn = sqlite3.connect('Masterbase.db')
    conn.row_factory = sqlite3.Row
    return conn

#Connect to the db and get the data
conn = get_db_connection()
param = "d_log_e_radio"
init_data = conn.execute("SELECT GRB, SNe, "+param+" from SQLDataGRBSNe").fetchall()
conn.close()

#Print the data
new_data = []
for i in range(len(init_data)):
    k = init_data[i][2]
    if str(init_data[i][2])!='None':
        k = str(init_data[i][2]).replace('E', 'e')


    a = [i, k]
    new_data.append(a)

#Update the db
conn = get_db_connection()
conn.executemany("UPDATE SQLDataGRBSNe SET "+param+" = ? WHERE rowid=?", ((i[1], i[0]+1,) for i in new_data))
conn.commit()
conn.close()