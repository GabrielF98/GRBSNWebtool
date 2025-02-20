'''
Reads a YAML file containing data about a GRB-SN event. Creates an SQL statement and logs that data in the database.
'''

import argparse
import sqlite3

import yaml

DB_PATH = "../static/Masterbase.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _load_yaml_config(yamlconfigfile):
    """
    Loads a user-supplied YAML file.
    """
    with open(yamlconfigfile, 'r', encoding='utf-8') as yaml_file:
        yamltxt = yaml_file.read()
        confyaml = yaml.load(yamltxt, Loader=yaml.SafeLoader)

    return confyaml


def build_query(table_name, yaml_dict):
    '''
    Generate the SQL query based on the dictionary key-value pairs.
    '''

    yaml_dict = yaml_dict[table_name]
    column_list = list(yaml_dict.keys())
    columns = ', '.join(column_list)
    sql = f'INSERT INTO {table_name} ({columns}) VALUES'
    values = [i for i in yaml_dict.values()]

    sql += '('
    for i in range(len(values)):
        if i < len(values)-1:
            sql += '?, '
        else:
            sql += '?'
    sql += ');'
    return sql, values


def dict2db(yaml_db_info):
    '''
    Create a connection to the DB.

    Transfer data from the dictionary to an SQL query, then add it to the DB.
    '''
    conn = get_db_connection()

    # INSERT for the SQLDataGRBSNe table.
    sql, values = build_query('SQLDataGRBSNe', yaml_db_info)
    conn.execute(sql, values)
    conn.commit()

    # INSERT for the PeakMagsTimes table.
    sql, values = build_query('PeakTimesMags', yaml_db_info)
    conn.execute(sql, values)
    conn.commit()

    # INSERT for the TrigCoords table.
    sql, values = build_query('TrigCoords', yaml_db_info)
    conn.execute(sql, values)
    conn.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Pass the location of the yaml file.')
    parser.add_argument('--file', type=str, required=False)
    args = parser.parse_args()
    yaml_db_info = _load_yaml_config(args.file)
    dict2db(yaml_db_info)
