trial_list = ['GRB000911', 'GRB011121-SN2001ke','GRB020305','GRB020405','GRB020410','GRB020903','GRB021211-SN2002lt','GRB030723','GRB030725','GRB041006']

import pandas as pd
import sqlite3

# Get the trigger time
def get_db_connection():
    conn = sqlite3.connect('static/Masterbase.db')
    conn.row_factory = sqlite3.Row
    return conn

# Return the trigtimes
def get_trigtime(event_id):
    # To determine if we need to search the db by SN or by GRB name
    conn = get_db_connection()
    if 'GRB' in event_id:
        #GRBs with SNs and without
        grb_name = event_id.split('-')[0][3:]

        # Table with triggertimes
        trigtime = conn.execute(
            'SELECT trigtime FROM TrigCoords WHERE grb_id=?', (grb_name,)).fetchall()

    # Lone SN cases
    elif 'SN' or 'AT' in event_id:
        sn_name = event_id[2:]

        # Table with triggertimes
        trigtime = conn.execute(
            'SELECT trigtime FROM TrigCoords WHERE sn_name=?', (sn_name,)).fetchall()

    conn.close()
    return trigtime

print(get_trigtime('GRB030725'))

# A function to parse date info. This will convert the date data to elapsed time since trigger.
# def elapsed_time(data, date_style, trigtime):
	# for i in data['date_unit']:
	# 	# Handle the different date formats
	# 	if str(i) = "yyyy-month-deciday":

	# 	elif str(i) = "yyyy-mm-deciday":
			
	# 	elif str(i) = "yyyy-mm-deciday-deciday":
			
	# 	elif str(i) = "yyyy-month-deciday-deciday":
			
	# 	elif str(i) = "yyyy-mm-dd-hh:mm-hh:mm":

	# 	elif str(i) = "MJD"