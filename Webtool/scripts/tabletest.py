'''
Prints the dataframe representation of a text file containing GRB-SN data.
Allows for quick identification of faults with the data standardisation.
'''
import os
import sys

import pandas as pd

SOURCE_DATA_PATH = "../static/SourceData/"

filename = sys.argv[1]

grbsn = str(filename).split('_', maxsplit=1)[0]

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

df = pd.read_csv(os.path.join(SOURCE_DATA_PATH, grbsn, filename), sep="\t")
print(df)
