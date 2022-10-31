import mysql.connector
db_conn = mysql.connector.connect(host="acit3855.westus3.cloudapp.azure.com", user="root",
password="password", database="events",auth_plugin='mysql_native_password')
db_cursor = db_conn.cursor()
db_cursor.execute('''
DROP TABLE ph_level, chlorine_level
''')
db_conn.commit()
db_conn.close()