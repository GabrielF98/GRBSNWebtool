import matplotlib.pyplot as plt
import numpy as np

import pandas as pd

data = pd.read_csv('tns_Ic-BLs_Feb22.csv')

redshift = data['Redshift']
sn_names = data['Name']


spec_IcBLs_with_GRBs = ['2016jca', '2017htp', '2017iuk', '2018fip', '2019jrj', '2020bvc', 'AT2019oyw']

#Number of SN events per year with and without GRBs
event_years_with = [1, 2, 1, 2, 1, 0, 0]

event_years_without = [0, 0, 0, 0, 0, 0, 0]


for i in sn_names:
	if i not in spec_IcBLs_with_GRBs:
		print(i[3:7])
		print(int(i[3:7])-2016)
		event_years_without[int(i[3:7])-2016]+=1

labels = ['2016', '2017', '2018', '2019', '2020', '2021', 'Feb. 2022']
width = 0.6

fig, ax = plt.subplots()

ax.bar(labels, event_years_without, width, color='green', alpha=0.5, label='Without GRB')
ax.bar(labels, event_years_with, width, color='purple', alpha=0.5, bottom=event_years_without, label='With GRB')

ax.set_ylabel('IcBLs/year')
ax.legend()
plt.yticks([0, 5, 10, 15, 20, 25])

plt.savefig('IcBLAssociationsNumberperyear(Bar).pdf') 