import sqlite3

conn = sqlite3.connect('readings.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE ph_level
          (id INTEGER PRIMARY KEY ASC, 
           location VARCHAR(250) NOT NULL,
           device_id VARCHAR(250) NOT NULL,
           phlevel VARCHAR(250) NOT NULL,
           temperature VARCHAR(250) NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           waterlevel INTEGER NOT NULL,
           trace_id VARCHAR(250) NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')

c.execute('''
          CREATE TABLE chlorine_level
          (id INTEGER PRIMARY KEY ASC,
           location VARCHAR(250) NOT NULL,
           device_id VARCHAR(250) NOT NUL
           chlorinelevel VARCHAR(250) NOT NULL,
           temperature VARCHAR(250) NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           waterlevel INTEGER NOT NULL,
           trace_id VARCHAR(250) NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')

conn.commit()
conn.close()

