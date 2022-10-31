import mysql.connector

db_conn = mysql.connector.connect(host="acit3855.westus3.cloudapp.azure.com", user="root",
password="password", database="events",auth_plugin='mysql_native_password')
db_cursor = db_conn.cursor()

db_cursor.execute('''
          CREATE TABLE ph_level
          (id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, 
           location VARCHAR(250) NOT NULL,
           device_id VARCHAR(250) NOT NULL,
           phlevel INTEGER NOT NULL,
           temperature INTEGER NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           waterlevel INTEGER NOT NULL,
           trace_id VARCHAR(250) NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')

db_cursor.execute('''
          CREATE TABLE chlorine_level
          (id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, 
           location VARCHAR(250) NOT NULL,
           device_id VARCHAR(250) NOT NULL,
           chlorinelevel INTEGER NOT NULL,
           temperature INTEGER NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           waterlevel INTEGER NOT NULL,
           trace_id VARCHAR(250) NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')

db_conn.commit()
db_conn.close()

