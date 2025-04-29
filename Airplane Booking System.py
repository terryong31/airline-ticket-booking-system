import mysql.connector 
import pandas as pd 
from sqlalchemy import create_engine
from IPython.display import display
from datetime import datetime
from seat_generator import seat_generator

db_connected = False
mydb = None
mycursor = None
engine = None
date_format = "%Y-%m-%d %H:%M:%S"

try:
    mydb = mysql.connector.connect(
        host = 'localhost', # Enter your own host name and other information
        port = 3306,
        user = 'root',
        password = '',
        database = 'airplane'
    )
    mycursor = mydb.cursor(buffered=True)
except Exception as err:
    print(f'SQL server connection cannot be established, please check XAMPP! Error Code: {err}')
    db_connected = False

try: 
    if mydb: 
        engine = create_engine('mysql+pymysql://root:@localhost:3306/airplane') # Same for this one
        db_connected = True
except Exception as err:
    print(f'SQLAlchemy engine creation failed. Please check pymysql or server. Error: {err}')
    db_connected = False
    engine = None

def Main():
    global db_connected, mydb, mycursor, engine, date_format
    while True:
        print('======================================================')
        print('       Welcome to AirAsia Ticket Booking System       ')
        print('======================================================')
        print('Are you a/an')
        print('(1) Admin or (2) User or (3) Quit')
        main_menu = input('Select one: ')
        match main_menu:
            case '1':
                status = admin_login(mycursor, mydb, engine)
                if status == 'logout':
                    continue
            case '2':
                status = user_login(mycursor, mydb, engine)
                if status == 'logout':
                    continue
            case '3':
                print('Goodbye!')
                mycursor.close()
                mydb.close()
                break
            case _:
                print('Invalid choice! Please select the correct one: ')

def admin_login(cursor, connection, engine):
    attempts = 3
    print('\nVerify Your Credentials')
    while attempts > 0:
        admin_id = input('Admin username: ')
        password = input('Enter password: ')
        query = "SELECT adminid, admin_password, admin_name FROM admin WHERE adminid= %s"
        mycursor.execute(query, (admin_id,))
        admininfo = mycursor.fetchone()
        if admininfo and password == admininfo[1]:
            print('Login successful! Redirecting...')
            admin = Admin(admin_id, admininfo[2], cursor, connection, engine)
            status = admin.admin_page()
            return status
        else:
            attempts -= 1
            print(f'\n    Wrong admin username or password! Please try again. You have {str(attempts)} attempt(s) left   \n')
    print('Too many failed attempts. Returning to main menu.')
    return None

def user_login(mycursor, mydb, engine):
    print('\nHi, welcome to AirAsia.')
    print('Would you like to')
    print('(1) Register an account')
    print('(2) Login with an existing account')
    print('(3) Exit')
    while True:
        x = input('Enter your selection: ')
        match x:
            case '1':
                return user_account_creation()
            case '2':
                attempts = 3
                print('\nVerify Your Credentials')
                while attempts > 0:
                    userid = input("What's your username: ")
                    password = input('Enter your password: ')
                    search_user_id = "SELECT userid, user_password, user_first_name, user_last_name FROM user WHERE userid= %s"
                    mycursor.execute(search_user_id, (userid,))
                    userinfo = mycursor.fetchone()
                    if userid == userinfo[0] and password == userinfo[1]:
                        print('Login successful! Directing...')
                        user = User(userinfo[0], userinfo[2], userinfo[3], mycursor, mydb, engine)
                        status = user.user_page()
                        return status
                    else:
                        attempts -= 1
                        print(f'\n    Wrong user username or password! Please try again. You have {str(attempts)} attempt(s) left   \n')
                    print('Too many attempts. Please try again later.\n')
                    return None
            case '3':
                print('\n')
                return None
            case _:
                print('Wrong input! Enter your selection (1-3)')

def user_account_creation():
    print('\nHello and thank you for registering a new account in AirAsia!')
    new_userid = input('Enter your user ID: ')
    query_check_username_availability = "SELECT userid FROM user WHERE userid = %s"
    mycursor.execute(query_check_username_availability, (new_userid,))
    check_username_availability = mycursor.fetchone()
    while True:
        if check_username_availability is None:
            return create_account_password_confirmation(new_userid)
        elif new_userid == check_username_availability[0]:
            new_userid = input('The username has been taken. Please enter another username: ')
            query_check_username_availability = "SELECT userid FROM user WHERE userid = %s"
            mycursor.execute(query_check_username_availability, (new_userid,))
            check_username_availability = mycursor.fetchone()
        
def create_account_password_confirmation(new_userid):
    new_password = input('Enter your password: ')
    confirm_new_password = input('Confirm password: ')
    while True:
        if new_password != confirm_new_password:
            new_password = input('Password do not match! Enter your password: ')
            confirm_new_password = input('Confirm password: ')
        elif new_password == confirm_new_password: 
            new_first_name = input('Enter your first name: ')
            new_last_name = input('Enter your last name: ')
            new_phone_number = input('Enter your phone number: ')
            query = "INSERT INTO user (userid, user_password, user_first_name, user_last_name, user_phone_number) VALUES (%s, %s, %s, %s, %s)"
            mycursor.execute(query, (new_userid, new_password, new_first_name, new_last_name, new_phone_number,))
            mydb.commit()
            print('\nAccount successfully created! Please login to use your account!')
            return user_login()

class Admin:
    def __init__(self, admin_id, admin_name, cursor, connection, engine):
        self.adminid = admin_id
        self.admin_name = admin_name
        self.cursor = cursor
        self.engine = engine
        self.connection = connection

    def admin_page(self):
        while True:
            print('\n======================================================')
            print('          Welcome to AirAsia Admin Dashboard          ') 
            print('======================================================')
            print(f'Welcome {self.admin_name}!')
            print('Enter your selection:')
            print('(1) Check user info')
            print('(2) Check tickets')
            print('(3) Manage flights')
            print('(4) Manage your account')
            print('(5) Logout')
            x = input('Enter your selection (1-5): ')
            match x:
                case '1':
                    self.admin_userinfo()
                case '2':
                    self.admin_checktickets()
                case '3':
                    self.admin_manageflights()
                case '4':
                    self.admin_manageaccount()
                case '5':
                    ask = input('Are you sure you want to logout? (Y/N): ').upper()
                    while True:
                        match ask:
                            case 'Y':
                                print('Successfully logout! Returning to dashboard... \n')
                                return 'logout'
                            case 'N':
                                return self.admin_page()
                        ask = input('Invalid Entry! Are you sure you want to logout? (Y/N): ')
                case _:
                    print('Invalid Selection!')

    def admin_userinfo(self):
        print('\n======================================================')
        print('Do you want to')
        print('(1) See all user information')
        print('(2) Search user information by ID')
        print('(3) Go Back')
        while True:
            x = input('Enter your selection: ')
            match x: 
                case '1':
                    all_users = pd.read_sql("SELECT userid, user_first_name, user_last_name, user_phone_number FROM user", engine)
                    print('')
                    if all_users.empty:
                        print('No users found.')
                    else:
                        display(all_users)
                    return self.admin_userinfo()
                case '2':
                    userid = input('Enter user ID: ')
                    query = """
                    SELECT 
                        u.userid, 
                        u.user_first_name, 
                        u.user_last_name, 
                        u.user_phone_number, 
                        GROUP_CONCAT(t.id SEPARATOR ', ') AS ticket_ids
                    FROM user u
                    LEFT JOIN ticket t ON u.userid = t.userid
                    WHERE u.userid = %s
                    GROUP BY u.userid, u.user_first_name, u.user_last_name, u.user_phone_number
                    """
                    everything = pd.read_sql(query, con = self.engine, params = (userid,))
                    everything = everything.drop(columns = ['userid'], errors = 'ignore')
                    if not everything.empty:
                        print('')
                        display(f'{everything}')
                        return self.admin_userinfo()
                    else:
                        print('\nNo user found!\n')
                        return self.admin_userinfo()
                case '3':
                    return
                case _:
                    print('Wrong selection! Please select the correct one (1-3)')

    def admin_checktickets(self):
        print('\n======================================================')
        print('Do you want to')
        print('(1) Check all tickets')
        print('(2) Search ticket by ID')
        print('(3) Search tickets by user ID')
        print('(4) Go Back')
        while True:
            x = input('Enter your selection: ')
            match x:
                case '1':
                    all_tickets = pd.read_sql("SELECT * FROM ticket", self.engine)
                    if all_tickets.empty: 
                        print('\nNo tickets found!')
                    else:
                        display(f'\n{all_tickets}')
                    return self.admin_checktickets()
                case '2':
                    ticketid = input('Enter ticket ID: ')
                    ticket = pd.read_sql("SELECT * FROM ticket WHERE id = %s", self.engine, params = (ticketid,))
                    if ticket.empty:
                        print('\nNo ticket found!')
                    else: 
                        display(f'\n{ticket}')
                    return self.admin_checktickets()
                case '3':
                    userid = input('Enter user ID: ')
                    ticket = pd.read_sql("SELECT * FROM ticket WHERE userid = %s", self.engine, params = (userid,))
                    if ticket.empty:
                        print('\nNo tickets found from this user')
                    else:
                        display(f'\n{ticket}')
                    return self.admin_checktickets()
                case '4':
                    return self.admin_page()
                case _:
                    print('Wrong input! Enter your selection again (1-4)')

    def admin_manageflights(self):
        print('\nDo you want to')
        print('1. See all flights')
        print('2. See all planes')
        print('3. Return')
        while True:
            selection = input('Enter your selection: ')
            match selection:
                case '1':
                    all_flights = pd.read_sql('SELECT * FROM flight_schedule', self.engine)
                    if all_flights.empty:
                        print('\nNo flights are available!')
                        return self.admin_manage_flight_dry()
                    else: 
                        display(f'\n{all_flights}')
                        return self.admin_manage_flight_dry()
                case '2':
                    all_plane = pd.read_sql('SELECT * FROM plane', self.engine)
                    if all_plane.empty:
                        print('\nNo planes found')
                        self.plane_management()
                    else:
                        print('')
                        display(all_plane)
                        self.plane_management()
                case '3':
                    return self.admin_page()
                case _:
                    print('Wrong Selection! Enter your selection again (1-3)')

    def admin_manage_flight_dry(self):
        print(f'\nDo you want to')
        print('1. Add a new flight schedule')
        print('2. Delete a flight schedule')
        print('3. Return')
        flight_selection = input('Enter your selection: ')
        while True:
            match flight_selection:
                case '1':
                    schedule_id = input("Enter a new schedule ID: ")
                    while True:
                        check_schedule_id_query = "SELECT schedule_id FROM flight_schedule WHERE schedule_id = %s"
                        self.cursor.execute(check_schedule_id_query, (schedule_id,))
                        check_schedule_id = self.cursor.fetchone()
                        if check_schedule_id is not None:
                            schedule_id = input('This schedule id already exist. Please pick another schedule id: ')
                        elif check_schedule_id is None:
                            break
                    destination = input('Enter destination (terminal code): ')
                    planeid = input('Enter plane ID: ')
                    plane_type_query = "SELECT plane_type FROM plane WHERE plane_id = %s"
                    self.cursor.execute(plane_type_query, (planeid,))
                    plane_type = self.cursor.fetchone()
                    if plane_type is None:
                        while True:
                            print('If you do not know the plane ID, enter "q" to exit.')
                            planeid = input('Plane ID does not exist. Please enter a valid plane ID: ')
                            plane_type_query = "SELECT plane_type FROM plane WHERE `plane_id` = %s"
                            self.cursor.execute(plane_type_query, (planeid,))
                            plane_type = self.cursor.fetchone()
                            plane_type_1 = plane_type[0]
                            if planeid == 'q':
                                return self.admin_manage_flight_dry()
                            elif plane_type is not None:
                                self.admin_manage_flight_dry_continue(schedule_id, planeid, destination, plane_type_1)
                    self.admin_manage_flight_dry_continue(schedule_id, planeid, destination, plane_type_1)
                case '2':
                    try: 
                        schedule_id = input('Enter the schedule ID to delete schedule: ')
                        schedule_query = "DELETE FROM flight_schedule WHERE schedule_id = %s"
                        self.cursor.execute(schedule_query, (schedule_id,))
                        seat_query = "DELETE FROM seats WHERE schedule_id = %s"
                        self.cursor.execute(seat_query, (schedule_id,))
                        self.connection.commit()
                        print('Flight schedule deleted successfully!')
                    except mysql.connector.Error as err:
                        self.connection.rollback()
                        print(f'An error occured! Please try again later or contact support! Error code: {err}')
                    return self.admin_manage_flight_dry()
                case '3':
                    print('Returning...')
                    return self.admin_manageflights()
                case _:
                    print('Wrong Input! Enter your selection (1-3)')

    def admin_manage_flight_dry_continue(self, schedule_id, planeid, destination, plane_type_1):
        try:
            unformatted_departure_date_time = input('Enter departure date & time (format: YYYY-MM-DD HH:MM:SS): ')
            departure_date_time = datetime.strptime(unformatted_departure_date_time, date_format)
        except ValueError:
            print('Invalid format! Please enter the date in the format DD-MM-YYYY HH:MM:SS (e.g., 2023-12-05 14:30:00).')
        terminal = input('Select terminal (terminal code): ')
        query = "INSERT INTO flight_schedule (schedule_id, plane_id, destination, departure_date_time, plane_type, terminal) VALUES (%s, %s, %s, %s, %s, %s)"
        self.cursor.execute(query, (schedule_id, planeid, destination, departure_date_time, plane_type_1, terminal,))
        self.connection.commit()
        seat_generator(planeid, schedule_id)
        self.connection.commit()
        print('Flight added successfully!')
        return self.admin_manage_flight_dry()

    def plane_management(self):
        print('\nDo you want to')
        print('(1) Add a new plane')
        print('(2) Delete a plane')
        print('(3) Return')
        plane_selection = input('Enter your selection: ')
        while True:
            match plane_selection:
                case '1':
                    plane_id = input('Enter new plane ID: ')
                    check_planeid_availability = "SELECT plane_id FROM plane WHERE plane_id = %s"
                    self.cursor.execute(check_planeid_availability, (plane_id,))
                    fetch = self.cursor.fetchone()
                    if fetch is None:
                            plane_name = input('Enter new plane name: ')
                            plane_query = "INSERT INTO plane (plane_id, plane_type) VALUES (%s, %s)"
                            self.cursor.execute(plane_query, (plane_id, plane_name))
                            self.connection.commit()
                            print('Plane added successfully!')
                            return self.plane_management()
                    while fetch[0] == plane_id:
                        plane_id = input('Plane ID already exist. Enter another plane ID: ')
                        check_planeid_availability = "SELECT plane_id FROM plane WHERE plane_id = %s"
                        self.cursor.execute(check_planeid_availability, (plane_id,))
                        fetch = self.cursor.fetchone()
                        if fetch is None:
                            plane_name = input('Enter new plane name: ')
                            plane_query = "INSERT INTO plane (plane_id, plane_type) VALUES (%s, %s)"
                            self.cursor.execute(plane_query, (plane_id, plane_name))
                            self.connection.commit()
                            print('Plane added successfully!')
                            return self.plane_management()
                case '2':
                    delete_plane = input('Enter plane ID to delete: ')
                    delete_plane_query = "DELETE FROM plane WHERE plane_id = %s"
                    self.cursor.execute(delete_plane_query, (delete_plane,))
                    self.connection.commit()
                    print('Plane deleted successfully!')
                    return self.plane_management()
                case '3':
                    print('Returning...')
                    return self.admin_manageflights()
                case _:
                    print('Wrong input! Enter your selection: ')
                
    def admin_manageaccount(self):
        while True:
            print('\n======================================================')
            print(f'You are currently logged in as {self.admin_name}')
            print('Do you want to')
            print('(1) Change your admin id')
            print('(2) Change your password')
            print('(3) Change your display name')
            print('(4) Go Back')
            x = input('Enter your selection: ')
            match x:
                case '1':
                    new_adminid = input('Enter your new admin ID: ')
                    updateadminid = "UPDATE admin SET adminid = %s WHERE adminid = %s"
                    self.cursor.execute(updateadminid, (new_adminid, self.adminid))
                    self.connection.commit()
                    print(f'ID successfully changed to {new_adminid}!')
                    return self.admin_manageaccount()
                case '2':
                    old_password = input('Enter your old password: ')
                    current_password = "SELECT admin_password FROM admin WHERE adminid = %s"
                    self.cursor.execute(current_password, (self.adminid,))
                    retrieve_password = self.cursor.fetchone()
                    if old_password == retrieve_password[0]:
                        new_password = input('Enter your new password: ')
                        updatepassword = "UPDATE admin SET admin_password = %s WHERE admin_password = %s"
                        self.cursor.execute(updatepassword, (new_password, old_password))
                        self.connection.commit()
                        print(f'Password successfully changed!')
                        return self.admin_manageaccount()
                    else:
                        print('Wrong password! Please try again later.')
                        return self.admin_manageaccount()
                case '3':
                    new_name = input('Enter your new display name: ')
                    updateadminname = "UPDATE admin SET admin_name = %s WHERE adminid = %s"
                    self.cursor.execute(updateadminname, (new_name, self.adminid))
                    self.connection.commit()
                    print(f'Name successfully changed to {new_name}!')
                    return self.admin_manageaccount()
                case '4':
                    return self.admin_page()
                case _:
                    print('Invalid selection! Enter your selection (1-4): ')

class User:
    def __init__(self, userid, user_first_name, user_last_name, cursor, connection, engine):
        self.userid = userid
        self.user_first_name = user_first_name
        self.user_last_name = user_last_name
        self.cursor = cursor
        self.connection = connection
        self.engine = engine

    def user_page(self):
        while True:
            print('\n======================================================')
            print('          Welcome to AirAsia User Dashboard          ') 
            print('======================================================')
            print(f'Welcome {self.user_first_name} {self.user_last_name}!')
            print('Enter your selection:')
            print('(1) Check flights')
            print('(2) Check tickets')
            print('(3) Cart')
            print('(4) Manage your account')
            print('(5) Logout')
            x = input('Enter your selection (1-5): ')
            match x:
                case '1':
                    return self.flight_dashboard()
                case '2':
                    return self.user_checktickets()
                case '3':
                    return self.user_cart()
                case '4':
                    return self.user_manageaccount()
                case '5':
                    ask = input('Are you sure you want to logout? (Y/N): ')
                    while True:
                        match ask:
                            case 'Y':
                                print('Successfully logout! Returning to dashboard... \n')
                                return 'logout'
                            case 'N':
                                return self.user_page()
                            case _:
                                print('Invalid Entry!')
                case _:    
                    print('Invalid Selection! Enter your selection (1-4)')

    def flight_dashboard(self):
        print('\n======================================================')
        print('               AirAsia Flight Dashboard               ') 
        print('======================================================')
        print('Enter these information below')
        print("Enter 'q' to exit")
        location = input('Travel Location (Enter Terminal Code): ')
        if location == 'q':
            return self.user_page()
        start_date = None
        while start_date is None:
            try:
                user_input = input('Start date & time (format: YYYY-MM-DD HH:MM:SS): ')
                start_date = datetime.strptime(user_input, date_format)
            except ValueError:
                print("Invalid format! Please enter the date in the format DD-MM-YYYY HH:MM:SS (e.g., 2023-12-05 14:30:00).")
        print("Enter 'q' to exit")
        returning = input('One way or returning? (O for one way and R for returning): ')
        while returning not in {'R', 'O', 'q'}:
            if returning == 'R':
                return self.show_returning_flight()
            elif returning == 'O':
                query = pd.read_sql("SELECT schedule_id, destination, departure_date_time, plane_type, terminal FROM flight_schedule WHERE destination = %s AND departure_date_time = %s", engine, params = (location, start_date,))
                if query.empty: 
                    print('\nNo flights found!')
                    return self.flight_dashboard()
                elif query is not None:
                    print(f'\n{len(query)} flight(s) are available.')
                    print(f'\n{query}')
                    return self.show_oneway_flight(location, start_date)
                else:
                    print('An error occured! Please try again later.')
                    return self.user_page()
            if returning == 'q':
                return self.user_page()
            returning = input('Invalid response! (O for one way and R for returning): ')

    def show_oneway_flight(self, location, start_date):
        confirmation = input('\nPlease select your desired flight plan by entering the schedule ID: ')
        sql = "SELECT seat_id, availability FROM seats WHERE schedule_id = %s"
        mycursor.execute(sql, (confirmation,))
        seat_layout = mycursor.fetchall()
        if seat_layout is None:
            print('Error finding seats.')
        rows = ['A', 'B', 'C', 'D']
        seats_per_row = 6
        seat_map = {}
        for seat_id, availability in seat_layout:
            seat_map[seat_id] = availability
        print('All seats are priced at RM100')
        print("\nSeating Layout (X = booked, O = available):")
        print("========Window=======")
        for row in rows:
            row_display = row + " "
            for num in range(1, seats_per_row + 1):
                seat_code = f"{row}{num}"
                if seat_code in seat_map:
                    row_display += " X " if seat_map[seat_code] == 0 else " O "
                else:
                    row_display += "   "
            print(row_display)
        print("========Window=======")
        while True:
            chosen_seat = input("Enter the seat ID you want to book (A1, B1, C1...): ")
            if seat_map.get(chosen_seat) == 1:
                add_to_cart = "INSERT INTO cart (user_id, destination, seat_id, schedule_id, departure_date_time) VALUES (%s, %s, %s, %s, %s)"
                mycursor.execute(add_to_cart, (self.userid, location, chosen_seat, confirmation, start_date,))
                mydb.commit()
                print('Added to cart successfully.')
                return self.user_page()
            elif seat_map.get(chosen_seat) == 0:
                chosen_seat = input("The seat is not available. Enter the seat ID you want to book (A1, B1, C1...): ")
            else:
                chosen_seat = input("Incorrect input. Enter the seat ID you want to book (A1, B1, C1...): ")
            
    def show_returning_flight(self, location, start_date):
        return_date = None
        while return_date is None:
            try:
                user_return_date = input('Start date & time (format: YYYY-MM-DD HH:MM:SS): ')
                return_date = datetime.strptime(user_return_date, date_format)
            except ValueError:
                print("Invalid format! Please enter the date in the format DD-MM-YYYY HH:MM:SS (e.g., 2023-12-05 14:30:00).")
        # For going one
        going_query = pd.read_sql("SELECT schedule_id, destination, departure_date_time, plane_type, terminal FROM flight_schedule WHERE destination = %s AND departure_date_time = %s", engine, params = (location, start_date,))
        if going_query is not None:
            print(f'\n{len(going_query)} going flight(s) are available.')
            print(f'\n{going_query}')
            going_confirmation = input('\nPlease select your desired flight going plan by entering the schedule ID: ')
            going_sql = "SELECT seat_id, availability FROM seats WHERE schedule_id = %s"
            mycursor.execute(going_sql, (going_confirmation,))
            going_seat_layout = mycursor.fetchall()
            if going_seat_layout is None:
                print('Error finding seats.')
            rows = ['A', 'B', 'C', 'D']
            seats_per_row = 6
            seat_map = {}
            for seat_id, availability in going_seat_layout:           
                seat_map[seat_id] = availability
            print('All seats are priced at RM100')
            print("\nSeating Layout (X = booked, O = available):")
            print("========Window=======")
            for row in rows:
                row_display = row + " "
                for num in range(1, seats_per_row + 1):
                    seat_code = f"{row}{num}"
                    if seat_code in seat_map:
                        row_display += " X " if seat_map[seat_code] == 0 else " O "
                    else:
                        row_display += "   "
                print(row_display)
            print("========Window=======")
            while True:
                chosen_seat = input("Enter the seat ID you want to add to cart (A1, B1, C1...): ")
                if seat_map.get(chosen_seat) == 1:
                    add_to_cart = "INSERT INTO cart (user_id, destination, seat_id, schedule_id, departure_date_time) VALUES (%s, %s, %s, %s, %s)"
                    mycursor.execute(add_to_cart, (self.userid, location, chosen_seat, going_confirmation, start_date,))
                    mydb.commit()
                    print('Added to cart successfully.')
                    # For returning one
                    returning_query = pd.read_sql("SELECT schedule_id, destination, departure_date_time, plane_type, terminal FROM flight_schedule WHERE destination IN ('PEN', 'KLIA1', 'KLIA2') AND departure_date_time = %s", engine, params = (return_date,))
                    print(f'{len(returning_query)} returning flights found!')
                    display(returning_query)
                    return_confirmation = input('Please enter your desired returning flight plan by entering the schedule ID: ')
                    returning_sql = "SELECT seat_id, availability FROM seats WHERE schedule_id = %s"
                    mycursor.execute(returning_sql, (return_confirmation,))
                    returning_seat_layout = mycursor.fetchall()
                    if returning_seat_layout is None:
                        print('Error finding seats.')
                    returning_rows = ['A', 'B', 'C', 'D']
                    returning_seats_per_row = 6
                    returning_seat_map = {}
                    for returning_seat_id, returning_availability in returning_seat_layout:           
                        returning_seat_map[returning_seat_id] = returning_availability
                    print('All seats are priced at RM100')
                    print("\nSeating Layout (X = booked, O = available):")
                    print("========Window=======")
                    for returning_row in returning_rows:
                        returning_row_display = returning_row + " "
                        for returning_num in range(1, returning_seats_per_row + 1):
                            returning_seat_code = f"{returning_row}{returning_num}"
                            if returning_seat_code in returning_seat_map:
                                returning_row_display += " X " if returning_seat_map[returning_seat_code] == 0 else " O "
                            else:
                                returning_row_display += "   "
                        print(returning_row_display)
                    print("========Window=======")
                    while True:
                        returning_chosen_seat = input("Enter the seat ID you want to add to cart (A1, B1, C1...): ")
                        if returning_seat_map.get(returning_chosen_seat) == 1:
                            returning_add_to_cart = "INSERT INTO cart (user_id, destination, seat_id, schedule_id, departure_date_time) VALUES (%s, %s, %s, %s, %s)"
                            mycursor.execute(returning_add_to_cart, (self.userid, location, returning_chosen_seat, return_confirmation, return_date,))
                            mydb.commit()
                            print('Added to cart successfully.')
                            return self.user_page()
                elif seat_map.get(chosen_seat) == 0:
                    chosen_seat = input("The seat is not available. Enter the seat ID you want to book (A1, B1, C1...): ")
                else:
                    chosen_seat = input("Incorrect input. Enter the seat ID you want to book (A1, B1, C1...): ")
                return self.show_returning_flight()
        else: 
            print('No flights found!')
            return self.flight_dashboard()

    def user_cart(self):
        print(f"\n{self.user_first_name}'s cart")
        all_cart = pd.read_sql("SELECT * FROM cart WHERE user_id = %s", engine, params=(self.userid,))
        if all_cart.empty:
            print('Your cart is empty')
        else:
            display(all_cart)
        print('\nDo you want to\n1) Check out\n2) Delete specific seat from cart')
        selection = input("Enter your selection (Enter 'q' to exit): ")
        while True:
            if selection == "1":
                return self.user_checkout()
            elif selection == "2":
                return self.user_delete_cart()
            elif selection == "q":
                return self.user_page()
            selection = input("Wrong input! Enter your selection (Enter 'q' to exit): ")
            
    def user_delete_cart(self):
        select_cart_id_to_delete = input("Enter your cart id to delete: ")
        check_availability_query = "SELECT cart_id FROM cart WHERE cart_id = %s"
        mycursor.execute(check_availability_query, (select_cart_id_to_delete,))
        check_availability = mycursor.fetchone()
        while True:
            if check_availability is not None:
                break
            if check_availability is None:
                select_cart_id_to_delete = input("Cart ID incorrect! Enter your cart id to delete: ")
                check_availability_query = "SELECT cart_id FROM cart WHERE cart_id = %s"
                mycursor.execute(check_availability_query, (select_cart_id_to_delete,))
                check_availability = mycursor.fetchone()
                while mycursor.nextset():
                    pass
        query = "DELETE FROM cart WHERE cart_id = %s"
        mycursor.execute(query, (select_cart_id_to_delete,))
        mydb.commit()
        print("Cart deleted successfully!")
        return self.user_cart()

    def user_checkout(self):
        select_cart_to_checkout = input(f'Enter cart ID to check out: ')
        while True:
            if select_cart_to_checkout == 'q':
                print('Returning to dashboard...')
                return self.user_page()
            cart_query = "SELECT * FROM cart WHERE cart_id = %s"
            mycursor.execute(cart_query, (select_cart_to_checkout,))
            fetch = mycursor.fetchone()
            while mycursor.nextset():
                pass
            if fetch is not None:
                break
            else:
                select_cart_to_checkout = input('No cart ID found! Enter cart ID to check out: ')
        confirmation = input('Are you sure you want to checkout (Y/N): ').upper()
        while confirmation not in ('Y', 'N'):
            confirmation = input('Wrong input! Are you sure you want to checkout (Y/N): ').upper()
        if confirmation == 'Y':
            correct_date_format = fetch[5].strftime("%Y-%m-%d %H:%M:%S")
            check_availability = "SELECT availability FROM seats WHERE schedule_id = %s"
            mycursor.execute(check_availability, (fetch[4],))
            availability = mycursor.fetchone()
            while mycursor.nextset():
                pass
            if availability[0] == 1:
                planeinfo = "SELECT * FROM flight_schedule WHERE schedule_id = %s"
                mycursor.execute(planeinfo, (fetch[4],))
                plane_info = mycursor.fetchone()
                while mycursor.nextset():
                    pass
                update_seat = "UPDATE seats SET availability = 0, booked_by = %s WHERE schedule_id = %s AND seat_id = %s"
                mycursor.execute(update_seat, (self.userid, fetch[4], fetch[3]))
                mydb.commit()
                add_ticket = "INSERT INTO ticket(userid, schedule_id, seat, time_date, plane_type, terminal, destination) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                mycursor.execute(add_ticket, (self.userid, fetch[4], fetch[3], correct_date_format,plane_info[4], plane_info[5], plane_info[2]))
                mydb.commit()
                update_cart = "DELETE FROM cart WHERE cart_id = %s"
                mycursor.execute(update_cart, (select_cart_to_checkout,))
                mydb.commit()
                print('Checkout successful!')
                return self.user_page()
            elif availability[0] == 0:
                print('Ticket is no longer available. Auto delete will be done.')
                auto_delete = "DELETE FROM cart WHERE cart_id = %s"
                mycursor.execute(auto_delete, (select_cart_to_checkout,))
                mydb.commit()
                return self.user_cart()
            else:
                print('An error has occurred. Please try again later.')
                return self.user_cart()
        elif confirmation == 'N':
            print('Checkout cancelled! Returning to cart...')
            return self.user_cart()

    def user_checktickets(self):
        print(f"\n{self.user_first_name} {self.user_last_name}'s tickets")
        all_tickets = pd.read_sql("SELECT * FROM ticket WHERE userid = %s", engine, params = (self.userid,))
        display(all_tickets)
        exit = input("\nEnter 'q' to exit: ")
        while True:
            if exit == 'q':
                return self.user_page()
            else:
                exit = input("Invalid entry! Please enter 'q' to exit: ")

    def user_manageaccount(self):
        print(f'\nManage your account')
        print(f'Do you want to')
        print(f'(1) Change display name')
        print(f'(2) Change username')
        print(f'(3) Change account password')
        print(f'(4) Return')
        while True:
            selection = input('Enter your selection: ')
            match selection:
                case '1':
                    new_first_name = input('Enter your new first name: ')
                    new_last_name = input('Enter your new last name: ')
                    query = "UPDATE user SET user_first_name = %s, user_last_name = %s WHERE userid = %s"
                    mycursor.execute(query, (new_first_name, new_last_name, self.userid,))
                    mydb.commit()
                    self.user_first_name = new_first_name
                    self.user_last_name = new_last_name
                    print('Name changed successfully!')
                    return self.user_manageaccount()
                case '2':
                    new_username = input('Enter your new username: ')
                    query_check_username_availability = "SELECT userid FROM user WHERE userid = %s"
                    mycursor.execute(query_check_username_availability, (new_username,))
                    check_username_availability = mycursor.fetchone()
                    while new_username == check_username_availability[0]:
                        new_username = input('Username is taken! Please enter another username: ')
                        query_check_username_availability = "SELECT userid FROM user WHERE userid = %s"
                        mycursor.execute(query_check_username_availability, (new_username,))
                        check_username_availability = mycursor.fetchone()
                        if check_username_availability == None:
                            break
                    query = "UPDATE user SET userid = %s where userid = %s"
                    mycursor.execute(query, (new_username, self.userid,))
                    mydb.commit()
                    self.userid = new_username
                    print('Username changed successfully!')
                    return self.user_manageaccount()
                case '3':
                    while True:
                        check = input('Enter your old password: ')
                        check_password = "SELECT user_password from user WHERE userid = %s"
                        mycursor.execute(check_password, (self.userid,))
                        old_password = mycursor.fetchone()
                        if check == old_password[0]:
                            new_password = input('Enter new password: ')
                            double_confirmation = input('Enter your new password again: ')
                            while new_password != double_confirmation:
                                if new_password == double_confirmation:
                                    new_password_query = "UPDATE user SET user_password = %s WHERE userid = %s"
                                    mycursor.execute(new_password_query, (new_password, self.userid))
                                    mydb.commit()
                                    print('Password changed successfully!')
                                    return self.user_manageaccount()
                                print('Password do not match!')
                                new_password = input('Enter new password: ')
                                double_confirmation = input('Enter your new password again: ')
                        elif check != old_password[0]:
                            check = input('Wrong old password! Enter your old password (Enter q to exit): ')
                            if check == 'q':
                                print('Returning...')
                                return self.user_manageaccount()
                case '4':
                    print('Returning to dashboard...')
                    return self.user_page()
                case _:
                    print('Wrong selection! Enter your selection again (1-4)')

Main()
