import sqlite3
import numpy as np

def get_db_connection():
    conn = sqlite3.connect('Masterbase.db')
    conn.row_factory = sqlite3.Row
    return conn

#Connect to the db and get the data
conn = get_db_connection()
init_data = conn.execute("SELECT e_iso from SQLDataGRBSNe").fetchall()
conn.close()

#Print the data
new_data = []
for i in init_data:
    print(i[0])
    new_data.append(str(i[0]).replace('E', 'e'))

#Update the db
conn = get_db_connection()
conn.executemany("UPDATE SQLDataGRBSNe SET e_iso = ?", ((i,) for i in new_data))
conn.commit()
conn.close()