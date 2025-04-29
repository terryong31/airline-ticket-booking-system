import mysql.connector

# just in case anything goes wrong with the mysql 'airplane' database just run this file
# remember to use your own connection host, port, user and password

conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password=""
)
cursor = conn.cursor()
cursor.execute("DROP DATABASE IF EXISTS airplane")
conn.commit()
print('Database deleted successfully!)
