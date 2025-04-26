import mysql.connector 
import pandas as pd 
from sqlalchemy import create_engine
from IPython.display import display
from datetime import datetime
from seat_generator import seat_generator

mydb = mysql.connector.connect(
    host = 'localhost', # Enter your own host name and other information
    port = 3306,
    user = 'root',
    password = '',
    database = 'airplane'
)

mycursor = mydb.cursor(buffered=True)
string = 'mysql+pymysql://root:@localhost:3306/airplane'
engine = create_engine(string)

def Main():
    print('======================================================')
    print('       Welcome to AirAsia Ticket Booking System       ')
    print('======================================================')
    print('Are you a/an')
    print('(1) Admin or (2) User or (3) Quit')
    main_menu = input('Select one: ')
    while main_menu != ['1', '2', '3']:
        if main_menu == '1':
            admin_login()
            break
        elif main_menu == '2':
            user_login()
            break
        elif main_menu == '3':
            print('Goodbye!')
            mycursor.close()
            mydb.close()
            return
        else:
            main_menu = input('Invalid choice! Please select the correct one: ')

def admin_login():
    attempts = 3
    print('\nVerify Your Credentials')
    while True:
        adminid = input('Admin username: ')
        password = input('Enter password: ')
        search_admin_id = "SELECT adminid, admin_password, admin_name FROM admin WHERE adminid= %s" # Retrieve admin id, password and name, also prevents SQL injection
        mycursor.execute(search_admin_id, (adminid,))
        admininfo = mycursor.fetchone()
        if admininfo is None:
            attempts -= 1
            print(f'\n    Wrong admin username or password! Please try again. You have {str(attempts)} attempt(s) left   \n')
        elif adminid == admininfo[0] and password == admininfo[1]:
            admin_name = admininfo[2]
            print('Login successful! Directing...')
            return admin_page(adminid, admin_name)
        else: 
            attempts -= 1
            print(f'\n    Wrong admin username or password! Please try again. You have {str(attempts)} attempt(s) left   \n')
        if attempts == 0:
            print('Too many attempts. Please try again later.\n')
            return Main()
            
def admin_page(adminid, admin_name):
    print('\n======================================================')
    print('          Welcome to AirAsia Admin Dashboard          ') 
    print('======================================================')
    print(f'Welcome {admin_name}!')
    print('Enter your selection:')
    print('(1) Check user info')
    print('(2) Check tickets')
    print('(3) Manage flights')
    print('(4) Manage your account')
    print('(5) Logout')
    x = input('Enter your selection (1-5): ')
    while x != ['1', '2', '3', '4', '5']:
        match x:
            case '1':
                return admin_userinfo(adminid, admin_name)
            case '2':
                return admin_checktickets(adminid, admin_name)
            case '3':
                return admin_manageflights(adminid, admin_name)
            case '4':
                return admin_manageaccount(adminid, admin_name)
            case '5':
                ask = input('Are you sure you want to logout? (Y/N): ')
                while ask != ['Y', 'N']:
                    match ask:
                        case 'Y':
                            print('Successfully logout! Returning to dashboard... \n')
                            return Main()
                        case 'N':
                            return admin_page(adminid, admin_name)
                    ask = input('Invalid Entry! Are you sure you want to logout? (Y/N): ')
        x = input('Invalid Selection! Enter your selection (1-4): ')

def admin_userinfo(adminid, admin_name):
    print('\n======================================================')
    print('Do you want to')
    print('(1) See all user information')
    print('(2) Search user information by ID')
    print('(3) Go Back')
    x = input('Enter your selection: ')
    while x != ['1', '2', '3']:
        match x: 
            case '1':
                all_users = pd.read_sql("SELECT userid, user_first_name, user_last_name, user_phone_number FROM user", engine)
                print('\n')
                if all_users.empty:
                    print('No users found.')
                else:
                    display(all_users)
                return admin_userinfo(adminid, admin_name)
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
                everything = pd.read_sql(query, con = engine, params = (userid,))
                everything = everything.drop(columns = ['userid'], errors = 'ignore')
                if not everything.empty:
                    print('\n')
                    display(everything)
                    return admin_userinfo(adminid, admin_name) 
                else:
                    print('\nNo user found!')
                    return admin_userinfo(adminid, admin_name) 
            case '3':
                return admin_page(adminid, admin_name)
        x = input('Incorrect choice! Enter your selection (1 or 2): ')

def admin_checktickets(adminid, admin_name):
    print('\n======================================================')
    print('Do you want to')
    print('(1) Check all tickets')
    print('(2) Search ticket by ID')
    print('(3) Search tickets by user ID')
    print('(4) Go Back')
    x = input('Enter your selection: ')
    while x != ['1', '2', '3', '4']:
        match x:
            case '1':
                all_tickets = pd.read_sql("SELECT * FROM ticket", engine)
                if all_tickets.empty: 
                    print('\nNo tickets found!')
                else:
                    display(all_tickets)
                return admin_checktickets(adminid, admin_name)
            case '2':
                ticketid = input('Enter ticket ID: ')
                ticket = pd.read_sql("SELECT * FROM ticket WHERE id = %s", engine, params = (ticketid,))
                if ticket.empty:
                    print('\nNo ticket found!')
                else: 
                    display(f'\n{ticket}')
                return admin_checktickets(adminid, admin_name)
            case '3':
                userid = input('Enter user ID: ')
                ticket = pd.read_sql("SELECT * FROM ticket WHERE userid = %s", engine, params = (userid,))
                if ticket.empty:
                    print('\nNo tickets found from this user')
                else:
                    display(f'\n{ticket}')
                return admin_checktickets(adminid, admin_name)
            case '4':
                return admin_page(adminid, admin_name)
        x = input('Wrong input! Enter your selection (1-4): ')
          
def admin_manage_flight_dry(adminid, admin_name):
    date_format = "%Y-%m-%d %H:%M:%S"
    print(f'\nDo you want to')
    print('1. Add a new flight schedule')
    print('2. Delete a flight schedule')
    print('3. Return')
    flight_selection = input('Enter your selection: ')
    while flight_selection != ['1', '2', '3']:
        if flight_selection == '1':
            schedule_id = input("Enter a new schedule ID: ")
            while True:
                check_schedule_id_query = "SELECT schedule_id FROM flight_schedule WHERE schedule_id = %s"
                mycursor.execute(check_schedule_id_query, (schedule_id,))
                check_schedule_id = mycursor.fetchone()
                if check_schedule_id is not None:
                    schedule_id = input('This schedule id already exist. Please pick another schedule id: ')
                    check_schedule_id_query = "SELECT schedule_id FROM flight_schedule WHERE schedule_id = %s"
                    mycursor.execute(check_schedule_id_query, (schedule_id,))
                    check_schedule_id = mycursor.fetchone()
                    return False
                elif check_schedule_id is None:
                    break
            destination = input('Enter destination (terminal code): ')
            planeid = input('Enter plane ID: ')
            plane_type_query = "SELECT plane_type FROM plane WHERE plane_id = %s"
            mycursor.execute(plane_type_query, (planeid,))
            plane_type = mycursor.fetchone()
            if plane_type is None:
                while True:
                    print('If you do not know the plane ID, enter "q" to exit.')
                    planeid = input('Plane ID does not exist. Please enter a valid plane ID: ')
                    plane_type_query = "SELECT plane_type FROM plane WHERE `plane_id` = %s"
                    mycursor.execute(plane_type_query, (planeid,))
                    plane_type = mycursor.fetchone()
                    if planeid == 'q':
                        return admin_manageflights(adminid, admin_name)
                    elif plane_type is not None:
                        unformatted_departure_date_time = input('Enter departure date & time (format: YYYY-MM-DD HH:MM:SS): ')
                        departure_date_time = datetime.strptime(unformatted_departure_date_time, date_format)
                        terminal = input('Select terminal (terminal code): ')
                        query = "INSERT INTO flight_schedule (schedule_id, plane_id, destination, departure_date_time, plane_type, terminal) VALUES (%s, %s, %s, %s, %s)"
                        mycursor.execute(query, (schedule_id, planeid, destination, departure_date_time, plane_type[0], terminal,))
                        seat_generator(planeid, schedule_id)
                        mydb.commit()
                        print('Flight added successfully!')
                        return admin_manageflights(adminid, admin_name)
            unformatted_departure_date_time = input('Enter departure date & time (format: YYYY-MM-DD HH:MM:SS): ')
            departure_date_time = datetime.strptime(unformatted_departure_date_time, date_format)
            terminal = input('Select terminal (terminal code): ')
            query = "INSERT INTO flight_schedule (schedule_id, plane_id, destination, departure_date_time, plane_type, terminal) VALUES (%s, %s, %s, %s, %s, %s)"
            mycursor.execute(query, (schedule_id, planeid, destination, departure_date_time, plane_type[0], terminal,))
            mydb.commit()
            seat_generator(planeid, schedule_id)
            mydb.commit()
            print('Flight added successfully!')
            return admin_manageflights(adminid, admin_name)
        elif flight_selection == '2':
            schedule_id = input('Enter the schedule ID to delete schedule: ')
            schedule_query = "DELETE FROM flight_schedule WHERE schedule_id = %s"
            mycursor.execute(schedule_query, (schedule_id,))
            seat_query = "DELETE FROM seats WHERE schedule_id = %s"
            mycursor.execute(seat_query, (schedule_id,))
            mydb.commit()
            print('Flight schedule deleted successfully!')
            return admin_manageflights(adminid, admin_name)
        elif flight_selection == '3':
            print('Returning...')
            return admin_manageflights(adminid, admin_name)

def admin_manageflights(adminid, admin_name):
    date_format = "%Y-%m-%d %H:%M:%S"
    print('\nDo you want to')
    print('1. See all flights')
    print('2. See all planes')
    print('3. Return')
    selection = input('Enter your selection: ')
    while selection != ['1', '2', '3']:
        match selection:
            case '1':
                all_flights = pd.read_sql('SELECT * FROM flight_schedule', engine)
                if all_flights.empty:
                    print('\nNo flights are available!')
                    admin_manage_flight_dry(adminid, admin_name)
                else: 
                    display(all_flights)
                    admin_manage_flight_dry(adminid, admin_name)
            case '2':
                all_plane = pd.read_sql('SELECT * FROM plane', engine)
                if all_plane.empty:
                    print('\nNo planes found')
                    print('\nDo you want to')
                    print('1. Add a new plane')
                    print('2. Delete a plane')
                    print('3. Return')
                    plane_selection = input('Enter your selection: ')
                    while plane_selection != ['1', '2', '3']:
                        if plane_selection == '1':
                            plane_id = input('Enter new plane ID: ')
                            check_planeid_availability = "SELECT plane_id FROM plane WHERE plane_id = %s"
                            mycursor.execute(check_planeid_availability, (plane_id,))
                            fetch = mycursor.fetchone()
                            if fetch is None:
                                    plane_name = input('Enter new plane name: ')
                                    plane_query = "INSERT INTO plane (plane_id, plane_type) VALUES (%s, %s)"
                                    mycursor.execute(plane_query, (plane_id, plane_name))
                                    mydb.commit()
                                    print('Plane added successfully!')
                                    return admin_manageflights(adminid, admin_name)
                            while fetch[0] == plane_id:
                                plane_id = input('Plane ID already exist. Enter another plane ID: ')
                                check_planeid_availability = "SELECT plane_id FROM plane WHERE plane_id = %s"
                                mycursor.execute(check_planeid_availability, (plane_id,))
                                fetch = mycursor.fetchone()
                                if fetch is None:
                                    plane_name = input('Enter new plane name: ')
                                    plane_query = "INSERT INTO plane (plane_id, plane_type) VALUES (%s, %s)"
                                    mycursor.execute(plane_query, (plane_id, plane_name))
                                    mydb.commit()
                                    print('Plane added successfully!')
                                    return admin_manageflights(adminid, admin_name)
                        elif plane_selection == '2':
                            delete_plane = input('Enter plane ID to delete: ')
                            delete_plane_query = "DELETE FROM plane WHERE plane_id = %s"
                            mycursor.execute(delete_plane_query, (delete_plane,))
                            mydb.commit()
                            print('Plane deleted successfully!')
                            pass
                        elif plane_selection == '3':
                            print('Returning...')
                            return admin_manageflights(adminid, admin_name)
                        else:
                            plane_selection = input('Wrong input! Enter your selection: ')
                else:
                    print('')
                    display(all_plane)
                    print('\nDo you want to')
                    print('1. Add a new plane')
                    print('2. Delete a plane')
                    print('3. Return')
                    plane_selection = input('Enter your selection: ')
                    while plane_selection != ['1', '2', '3']:
                        if plane_selection == '1':
                            plane_id = input('Enter new plane ID: ')
                            plane_name = input('Enter new plane name: ')
                            plane_query = "INSERT INTO plane (plane_id, plane_type) VALUES (%s, %s)"
                            mycursor.execute(plane_query, (plane_id, plane_name))
                            mydb.commit()
                            print('Plane added successfully!')
                            return admin_manageflights(adminid, admin_name)
                        elif plane_selection == '2':
                            delete_plane = input('Enter plane ID to delete: ')
                            delete_plane_query = "DELETE FROM plane WHERE plane_id = %s"
                            mycursor.execute(delete_plane_query, (delete_plane,))
                            mydb.commit()
                            print('Plane deleted successfully!')
                            pass
                        elif plane_selection == '3':
                            print('Returning...')
                            return admin_manageflights(adminid, admin_name)
                        else:
                            plane_selection = input('Wrong input! Enter your selection: ')
            case '3':
                return admin_page(adminid, admin_name)
        selection = input('Wrong input! Enter your selection (1-3): ')
                
def admin_manageaccount(adminid, admin_name):
    print('\n======================================================')
    print(f'You are currently logged in as {admin_name}')
    print('Do you want to')
    print('(1) Change your admin id')
    print('(2) Change your password')
    print('(3) Change your display name')
    print('(4) Go Back')
    x = input('Enter your selection: ')
    while x != ['1', '2', '3', '4']:
        match x:
            case '1':
                new_adminid = input('Enter your new admin ID: ')
                updateadminid = "UPDATE admin SET adminid = %s WHERE adminid = %s"
                mycursor.execute(updateadminid, (new_adminid, adminid))
                mydb.commit()
                print(f'ID successfully changed to {new_adminid}!')
                return admin_manageaccount(new_adminid, admin_name)
            case '2':
                old_password = input('Enter your old password: ')
                current_password = "SELECT admin_password FROM admin WHERE adminid = %s"
                mycursor.execute(current_password, (adminid,))
                retrieve_password = mycursor.fetchone()
                if old_password == retrieve_password[0]:
                    new_password = input('Enter your new password: ')
                    updatepassword = "UPDATE admin SET admin_password = %s WHERE admin_password = %s"
                    mycursor.execute(updatepassword, (new_password, old_password))
                    mydb.commit()
                    print(f'Password successfully changed!')
                    return admin_manageaccount(adminid, admin_name)
                else:
                    print('Wrong password! Please try again later.')
                    return admin_manageaccount(adminid, admin_name)
            case '3':
                new_name = input('Enter your new display name: ')
                updateadminname = "UPDATE admin SET admin_name = %s WHERE adminid = %s"
                mycursor.execute(updateadminname, (new_name, adminid))
                mydb.commit()
                print(f'Name successfully changed to {new_name}!')
                return admin_manageaccount(adminid, new_name)
            case '4':
                return admin_page(adminid, admin_name)
        x = input('Invalid selection! Enter your selection (1-4): ')
    
def user_login():
    print('\nHi, welcome to AirAsia.')
    print('Would you like to')
    print('(1) Register an account')
    print('(2) Login with an existing account')
    print('(3) Exit')
    x = input('Enter your selection: ')
    while x != ['1', '2', '3']: 
        match x:
            case '1':
                return user_account_creation()
            case '2':
                attempts = 3
                print('\nVerify Your Credentials')
                while True:
                    userid = input("What's your username: ")
                    password = input('Enter your password: ')
                    search_user_id = "SELECT userid, user_password, user_first_name, user_last_name FROM user WHERE userid= %s"
                    mycursor.execute(search_user_id, (userid,))
                    userinfo = mycursor.fetchone()
                    if userinfo == None:
                        attempts -= 1
                        print(f'\n    Wrong user username or password! Please try again. You have {str(attempts)} attempt(s) left   \n')
                    elif userid != userinfo[0] or password != userinfo[1]: 
                        attempts -= 1
                        print(f'\n    Wrong user username or password! Please try again. You have {str(attempts)} attempt(s) left   \n')
                    elif userid == userinfo[0] and password == userinfo[1]:
                        print('Login successful! Directing...')
                        return user_page(userid, userinfo[2], userinfo[3])
                    if attempts == 0:
                        print('Too many attempts. Please try again later.\n')
                        return user_login()
            case '3':
                print('\n')
                return Main()
        x = input('Wrong input! Enter your selection (1-3): ')  

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

def user_page(userid, user_first_name, user_last_name):
    print('\n======================================================')
    print('          Welcome to AirAsia User Dashboard          ') 
    print('======================================================')
    print(f'Welcome {user_first_name} {user_last_name}!')
    print('Enter your selection:')
    print('(1) Check flights')
    print('(2) Check tickets')
    print('(3) Cart')
    print('(4) Manage your account')
    print('(5) Logout')
    x = input('Enter your selection (1-5): ')
    while x != {'1', '2', '3', '4', '5'}:
        match x:
            case '1':
                return flight_dashboard(userid, user_first_name, user_last_name)
            case '2':
                return user_checktickets(userid, user_first_name, user_last_name)
            case '3':
                return user_cart(userid, user_first_name, user_last_name)
            case '4':
                return user_manageaccount(userid, user_first_name, user_last_name)
            case '5':
                ask = input('Are you sure you want to logout? (Y/N): ')
                while ask != ['Y', 'N']:
                    match ask:
                        case 'Y':
                            print('Successfully logout! Returning to dashboard... \n')
                            return Main()
                        case 'N':
                            return user_page(userid, user_first_name, user_last_name)
                    ask = input('Invalid Entry! Are you sure you want to logout? (Y/N): ')
        x = input('Invalid Selection! Enter your selection (1-4): ')

def flight_dashboard(userid, user_first_name, user_last_name):
    date_format = "%Y-%m-%d %H:%M:%S"
    print('\n======================================================')
    print('               AirAsia Flight Dashboard               ') 
    print('======================================================')
    print('Enter these information below')
    print("Enter 'q' to exit")
    location = input('Travel Location (Enter Terminal Code): ')
    if location == 'q':
        return user_page(userid, user_first_name, user_last_name)
    start_date = None
    while start_date is None:
        try:
            user_input = input('Start date & time (format: YYYY-MM-DD HH:MM:SS): ')
            start_date = datetime.strptime(user_input, date_format)
        except ValueError:
            print("Invalid format! Please enter the date in the format DD-MM-YYYY HH:MM:SS (e.g., 2023-12-05 14:30:00).")
    print("Enter 'q' to exit")
    returning = input('One way or returning? (O for one way and R for returning): ')
    while returning != ['R', 'O', 'q']:
        if returning == 'R':
            return show_returning_flight(userid, location, start_date, user_first_name, user_last_name, date_format)
        elif returning == 'O':
            query = pd.read_sql("SELECT schedule_id, destination, departure_date_time, plane_type, terminal FROM flight_schedule WHERE destination = %s AND departure_date_time = %s", engine, params = (location, start_date,))
            if query.empty: 
                print('\nNo flights found!')
                return flight_dashboard(userid, user_first_name, user_last_name)
            elif query is not None:
                print(f'\n{len(query)} flight(s) are available.')
                print(f'\n{query}')
                return show_oneway_flight(userid, location, start_date, user_first_name, user_last_name)
            else:
                print('An error occured! Please try again later.')
                return user_page(userid, user_first_name, user_last_name)
        if returning == 'q':
            return user_page(userid, user_first_name, user_last_name)
        returning = input('Invalid response! (O for one way and R for returning): ')

def show_oneway_flight(userid, location, start_date, user_first_name, user_last_name):
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
            mycursor.execute(add_to_cart, (userid, location, chosen_seat, confirmation, start_date,))
            mydb.commit()
            print('Added to cart successfully.')
            return user_page(userid, user_first_name, user_last_name)
        elif seat_map.get(chosen_seat) == 0:
            chosen_seat = input("The seat is not available. Enter the seat ID you want to book (A1, B1, C1...): ")
        else:
            chosen_seat = input("Incorrect input. Enter the seat ID you want to book (A1, B1, C1...): ")
            
        
def show_returning_flight(userid, location, start_date, user_first_name, user_last_name, date_format):
    date_format = "%Y-%m-%d %H:%M:%S"
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
                mycursor.execute(add_to_cart, (userid, location, chosen_seat, going_confirmation, start_date,))
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
                        mycursor.execute(returning_add_to_cart, (userid, location, returning_chosen_seat, return_confirmation, return_date,))
                        mydb.commit()
                        print('Added to cart successfully.')
                        return user_page(userid, user_first_name, user_last_name)
            elif seat_map.get(chosen_seat) == 0:
                chosen_seat = input("The seat is not available. Enter the seat ID you want to book (A1, B1, C1...): ")
            else:
                chosen_seat = input("Incorrect input. Enter the seat ID you want to book (A1, B1, C1...): ")
            return show_returning_flight(userid, location, start_date, user_first_name, user_last_name, date_format)
    else: 
        print('No flights found!')
        return flight_dashboard(userid, user_first_name, user_last_name)

def user_cart(userid, user_first_name, user_last_name):
    print(f"\n{user_first_name}'s cart")
    all_cart = pd.read_sql("SELECT * FROM cart WHERE user_id = %s", engine, params=(userid,))
    if all_cart.empty:
        print('Your cart is empty')
    else:
        display(all_cart)
    print('\nDo you want to\n1) Check out\n2) Delete specific seat from cart')
    selection = input("Enter your selection (Enter 'q' to exit): ")
    while True:
        if selection == "1":
            return user_checkout(userid, user_first_name, user_last_name)
        elif selection == "2":
            return user_delete_cart(userid, user_first_name, user_last_name)
        elif selection == "q":
            return user_page(userid, user_first_name, user_last_name)
        selection = input("Wrong input! Enter your selection (Enter 'q' to exit): ")
        
def user_delete_cart(userid, user_first_name, user_last_name):
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
    return user_cart(userid, user_first_name, user_last_name)

def user_checkout(userid, user_first_name, user_last_name):
    select_cart_to_checkout = input(f'Enter cart ID to check out: ')
    while True:
        if select_cart_to_checkout == 'q':
            print('Returning to dashboard...')
            return user_page(userid, user_first_name, user_last_name)
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
            mycursor.execute(update_seat, (userid, fetch[4], fetch[3]))
            mydb.commit()
            add_ticket = "INSERT INTO ticket(userid, schedule_id, seat, time_date, plane_type, terminal, destination) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            mycursor.execute(add_ticket, (userid, fetch[4], fetch[3], correct_date_format,plane_info[4], plane_info[5], plane_info[2]))
            mydb.commit()
            update_cart = "DELETE FROM cart WHERE cart_id = %s"
            mycursor.execute(update_cart, (select_cart_to_checkout,))
            mydb.commit()
            print('Checkout successful!')
            return user_page(userid, user_first_name, user_last_name)
        elif availability[0] == 0:
            print('Ticket is no longer available. Auto delete will be done.')
            auto_delete = "DELETE FROM cart WHERE cart_id = %s"
            mycursor.execute(auto_delete, (select_cart_to_checkout,))
            mydb.commit()
            return user_cart(userid, user_first_name, user_last_name)
        else:
            print('An error has occurred. Please try again later.')
            return user_cart(userid, user_first_name, user_last_name)
    elif confirmation == 'N':
        print('Checkout cancelled! Returning to cart...')
        return user_cart(userid, user_first_name, user_last_name)

def user_checktickets(userid, user_first_name, user_last_name):
    print(f"\n{user_first_name} {user_last_name}'s tickets")
    all_tickets = pd.read_sql("SELECT * FROM ticket WHERE userid = %s", engine, params = (userid,))
    display(all_tickets)
    exit = input("\nEnter 'q' to exit: ")
    while True:
        if exit == 'q':
            return user_page(userid, user_first_name, user_last_name)
        else:
            exit = input("Invalid entry! Please enter 'q' to exit: ")

def user_manageaccount(userid, user_first_name, user_last_name):
    print(f'\nManage your account')
    print(f'Do you want to')
    print(f'1. Change display name')
    print(f'2. Change username')
    print(f'3. Change account password')
    print(f'4. Return')
    selection = input('Enter your selection: ')
    while selection != ['1', '2', '3', '4']:
        match selection:
            case '1':
                new_first_name = input('Enter your new first name: ')
                new_last_name = input('Enter your new last name: ')
                query = "UPDATE user SET user_first_name = %s, user_last_name = %s WHERE userid = %s"
                mycursor.execute(query, (new_first_name, new_last_name, userid,))
                mydb.commit()
                print('Name changed successfully!')
                return user_manageaccount(userid, new_first_name, new_last_name)
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
                mycursor.execute(query, (new_username, userid,))
                mydb.commit()
                print('Username changed successfully!')
                return user_manageaccount(new_username, user_first_name, user_last_name)
            case '3':
                while True:
                    check = input('Enter your old password: ')
                    check_password = "SELECT user_password from user WHERE userid = %s"
                    mycursor.execute(check_password, (userid,))
                    old_password = mycursor.fetchone()
                    if check == old_password[0]:
                        new_password = input('Enter new password: ')
                        double_confirmation = input('Enter your new password again: ')
                        while new_password != double_confirmation:
                            if new_password == double_confirmation:
                                new_password_query = "UPDATE user SET user_password = %s WHERE userid = %s"
                                mycursor.execute(new_password_query, (new_password, userid))
                                mydb.commit()
                                print('Password changed successfully!')
                                return user_manageaccount(userid, user_first_name, user_last_name)
                            print('Password do not match!')
                            new_password = input('Enter new password: ')
                            double_confirmation = input('Enter your new password again: ')
                    elif check != old_password[0]:
                        check = input('Wrong old password! Enter your old password (Enter q to exit): ')
                        if check == 'q':
                            print('Returning...')
                            return user_manageaccount(userid, user_first_name, user_last_name)
            case '4':
                print('Returning to dashboard...')
                return user_page(userid, user_first_name, user_last_name)
        selection = input('Wrong selection! Enter your selection again (1-4): ')   

Main()