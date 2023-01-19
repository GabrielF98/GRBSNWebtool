import matplotlib.pyplot as plt
import numpy as np

import pandas as pd

data = pd.read_csv('tns_IcBLs_Nov22022.csv')

redshift = data['Redshift']
sn_names = data['Name']

# spec_IcBLs_with_GRBs = ['2016jca', '2017htp', '2017iuk', '2018fip', '2019jrj', '2020bvc', 'AT2019oyw']

#Number of SN events per year with and without GRBs
event_years_with = [1, 2, 1, 2, 1, 0, 1] # SpecGRB
event_years_with_grb = [0, 0, 0, 0, 2, 1, 1] # PhotGRB
event_years_without = [0, 0, 0, 0, 0, 0, 0]

#Loop over the names of the Ic-BLs
for i in sn_names:
	print(i)
	print(int(i[3:7])-2016)
	event_years_without[int(i[3:7])-2016]+=1

for i in range(len(event_years_without)):
	event_years_without[i] = event_years_without[i]-event_years_with[i]

labels = ['2016', '2017', '2018', '2019', '2020', '2021', 'Nov. 22']
width = 0.6

fig, ax = plt.subplots()
plt.rcParams.update({'font.size': 14})

ax.bar(labels, event_years_without, width, color='green', alpha=0.5, label='Without GRB')
ax.bar(labels, event_years_with, width, color='purple', alpha=0.5, bottom=event_years_without, label='With GRB (spec)')
ax.bar(labels, event_years_with_grb, width, color='#FF07CC', alpha=0.5, bottom=np.array(event_years_with)+np.array(event_years_without), label='With GRB (phot)')

ax.set_ylabel('IcBLs/year', size=15)
ax.legend(loc = 'best')
plt.yticks([0, 5, 10, 15, 20, 25], size=15)
plt.ylim([0, 28])
plt.xticks(size=14)

plt.savefig('IcBLAssociations4Paper.pdf') 