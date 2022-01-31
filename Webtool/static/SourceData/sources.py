import pandas as pd
import numpy as np
import os

df = pd.read_csv('sourcelist.csv') #import the data

root = os.getcwd()
dirs = [ item for item in os.listdir(root) if os.path.isdir(os.path.join(root, item)) ]

for i in dirs:
	df2 = df.loc[df['GRB/SN'] == i]
	df2.to_csv('./'+str(i)+'/'+str(i)+'filesources.csv', sep=',', index=False)