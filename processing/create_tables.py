import sqlite3
import datetime

conn = sqlite3.connect('stats.sqlite')

c = conn.cursor()
c.execute('''
    CREATE TABLE stats
    (id INTEGER PRIMARY KEY ASC,
    num_phlevel_reading INTEGER NOT NULL,
    max_phlevel_reading INTEGER NOT NULL,
    max_water_level INTEGER,
    max_chlorine_level INTEGER,
    num_chlorine_level INTEGER,
    last_updated VARCHAR(100) NOT NULL)
''')
conn.commit()
conn.close()


