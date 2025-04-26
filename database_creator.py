import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password=""
)
cursor = conn.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS airplane")
conn.commit()

conn.database = "airplane"

cursor.execute("""
CREATE TABLE IF NOT EXISTS admin (
    adminid VARCHAR(8) PRIMARY KEY,
    admin_name VARCHAR(50),
    admin_password VARCHAR(50),
    admin_phone_number VARCHAR(50)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS user (
    userid VARCHAR(50) PRIMARY KEY,
    user_password VARCHAR(50),
    user_first_name VARCHAR(50),
    user_last_name VARCHAR(50),
    user_phone_number VARCHAR(50)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS plane (
    plane_id VARCHAR(5) PRIMARY KEY,
    plane_type VARCHAR(50)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS flight_schedule (
    schedule_id VARCHAR(5) PRIMARY KEY,
    plane_id VARCHAR(5),
    destination VARCHAR(10),
    departure_date_time DATETIME,
    plane_type VARCHAR(30),
    terminal VARCHAR(10),
    FOREIGN KEY (plane_id) REFERENCES plane(plane_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS cart (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50),
    destination VARCHAR(10),
    seat_id TEXT,
    schedule_id VARCHAR(5),
    departure_date_time DATETIME,
    FOREIGN KEY (user_id) REFERENCES user(userid),
    FOREIGN KEY (schedule_id) REFERENCES flight_schedule(schedule_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS seats (
    schedule_id VARCHAR(5),
    plane_id VARCHAR(5),
    seat_id VARCHAR(10),
    availability BOOLEAN DEFAULT 1,
    booked_by VARCHAR(50),
    PRIMARY KEY(seat_id, schedule_id),
    FOREIGN KEY (schedule_id) REFERENCES flight_schedule(schedule_id),
    FOREIGN KEY (plane_id) REFERENCES plane(plane_id),
    FOREIGN KEY (booked_by) REFERENCES user(userid)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS ticket (
    id INT(10) AUTO_INCREMENT PRIMARY KEY,
    userid VARCHAR(50),
    schedule_id VARCHAR(5),
    seat VARCHAR(50),
    time_date DATETIME,
    plane_type VARCHAR(50),
    terminal VARCHAR(50),
    destination VARCHAR(50),
    FOREIGN KEY (userid) REFERENCES user(userid),
    FOREIGN KEY (schedule_id) REFERENCES flight_schedule(schedule_id)
)
""")

cursor.execute("""
INSERT INTO admin (adminid, admin_name, admin_password, admin_phone_number) VALUES ('admin', 'admin', 'admin','0123456789')       
""")

conn.commit()
cursor.close()
conn.close()

print("Database and all tables created successfully.")