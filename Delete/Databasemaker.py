import sqlite3

#Create the place the database is stored
conn = sqlite3.connect('GRB-SNe.db')
c = conn.cursor

c = conn.cursor()

# Create table
c.execute('''CREATE TABLE meta
             (grb text, sne text, log_e_iso real, p real, log_n real,\
              log_eps_e real, log_eps_b real, obs_deg real, open_deg real, \
              ej_M real, ni_M real)''')

grb = input('GRB Name:') 
sne = input('SNe Name:')
log_e_iso = input('log_e_iso:')
p = input('p:') 
log_n = input('log_n:')
log_eps_e = input('log_eps_e:')
log_eps_b = input('log_eps_b:')
obs_deg = input('obs_deg:')
open_deg = input('open_deg:')
ej_M = input('ej_M:')
ni_M = input('ni_M:')

# Insert a row of data
c.execute("INSERT INTO meta VALUES (?,?,?,?,?,?,?,?,?,?,?)", (grb, sne, \
	log_e_iso, p, log_n, log_eps_e, log_eps_b, obs_deg, open_deg, ej_M, ni_M))

# Save (commit) the changes
conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()