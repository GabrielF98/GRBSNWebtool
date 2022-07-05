import pandas as pd 
import sys

filename = sys.argv[1] 

grbsn = str(filename).split('_')[0]

df = pd.read_csv(grbsn+'/'+filename, sep='\t')
print(df)