import glob

import pandas as pd

filename = glob.glob('NotionExport/Webtool*/Source List*.csv')

df = pd.read_csv(filename[0])
df.to_csv("tags.csv", index=False)