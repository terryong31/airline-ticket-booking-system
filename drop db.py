import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password=""
)
cursor = conn.cursor()

cursor.execute("DROP DATABASE IF EXISTS airplane")
conn.commit()