import mysql.connector 

mydb = mysql.connector.connect(
    host = 'localhost',
    port = 3306,
    user = 'root',
    password = '',
    database = 'airplane'
)

mycursor = mydb.cursor()

def seat_generator(planeid, schedule_id):
    rows = ['A', 'B', 'C', 'D']
    column = 6

    for row in rows:    
        for num in range(1, column + 1):
            seat = f"{row}{num}"
            availability = 1
            query = "INSERT INTO seats (schedule_id, plane_id, seat_id, availability) VALUES (%s, %s, %s, %s)"
            mycursor.execute(query, (schedule_id, planeid, seat, availability))
            mydb.commit()
    print('Seat Created Successfully!')