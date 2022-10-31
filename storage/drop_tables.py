import sqlite3

conn = sqlite3.connect('readings.sqlite')

c = conn.cursor()
c.execute('''
          DROP TABLE  ph_level
          ''')
c.execute('''
          DROP TABLE  chlorine_level
          ''')

conn.commit()
conn.close()
