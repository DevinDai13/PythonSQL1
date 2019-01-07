import sqlite3
import hashlib
import AdminControls

# First connect to the database
# I am terrible at OOP
sqlite_file = 'waste_management.db'
conn = sqlite3.connect(sqlite_file)
c = conn.cursor()


# Identifiers for pbkdf2_hmac that must not be changed
# Salting the password is random and gives extra protection
# Iterations tells you how many times to iterate before execution = slower rainbow tables
def encodepassword(password):
    hash_name = 'sha256'
    salt = 'ssdirf993lksiqb4'
    iterations = 100000
    dk = hashlib.pbkdf2_hmac(hash_name, bytearray(password, 'ascii'), bytearray(salt, 'ascii'), iterations)
    return dk


# Part of the login screen, asks the user to input their password and username
def login(username):
    password = input("Please enter your password")
    user_id = get_id(username)
    if user_id == 0:
        return False
    encoded_password = encodepassword(password)
    database_password = str(get_password(user_id))

    if authenticate(encoded_password, database_password):
        return True
    else:
        return False


# Check to see if the inputted password is the same as the stored password
def authenticate(entered_password, database_password):
    if str(entered_password) == str(database_password):
        print("Acess Granted\n")
        return True
    else:
        print(entered_password)
        print(database_password)
        print("Access Denied\n")
        return False


# Get password from the user_id, could also be username since they are both unique
def get_password(user_id):
    c.execute('SELECT password FROM users WHERE user_id = {id}'.format(id=user_id))
    return c.fetchone()[0]


# Get the role of the user
def get_role(username):
    c.execute('SELECT role FROM users WHERE login = "{id}"'.format(id=username))
    return c.fetchone()


# Get the id of the user
def get_id(username):
    c.execute('SELECT user_id FROM users WHERE login = "{id}"'.format(id=username))
    username_1 = c.fetchone()
    if username_1:
        return username_1[0]
    else:
        print("User does not exist")
        return 0


# Create a unique account id for the account
def create_unique_account_id():
    c.execute('select max(account_no) from account')
    account_no = c.fetchone()
    if account_no:
        return int(account_no[0]) + 1
    else:
        return 1


# ----------Each user is a separate class, they will all have a main method used to loop the other methods-------------

# No need to store password here
# Class used for inheritance
class Personnel:
    def __init__(self, user_id, username, role):
        self.user_id = user_id
        self.login = username
        self.role = role


# Account managers use the system to query and update information about the accounts they manage
class AccountManager(Personnel):

    def __init__(self, user_id, username, role):
        Personnel.__init__(self, user_id, username, role)

    # Control method is used by the accountmgr to pick their desired method
    def main(self):

        logout_role = False
        print("You are logged in as an Account Manager")

        while not logout_role:
            print("Enter a following command (By Number): ")
            print("1: Select a customer")
            print("2: Create a customer account")
            print("3: Create a new service agreement")
            print("4: Select a summary report to be printed")
            command = input("5: To logout\n")

            try:
                if int(command) == 1:
                    self.selectcustomer()
                    conn.commit()

                if int(command) == 2:
                    self.createaccount()
                    conn.commit()

                if int(command) == 3:
                    self.newserviceagreement()
                    conn.commit()

                if int(command) == 4:
                    self.summaryreport()
                    conn.commit()

                if int(command) == 5:
                    logout_role = True

            except TypeError:
                print("Invalid command")

        return 0

    # Select and list an account that the manager manages
    def selectcustomer(self):

        customer = input("Enter the customer's account number")
        c.execute("select * from accounts "
                  "where account_no = '{account_num}'"
                  "and account_mgr = '{account_manager}'"
                  .format(account_num=int(customer), account_manager=int(self.user_id)))

        id = c.fetchall()
        for customer in id:
            print(customer)

        if id:
            c.execute('select * from service_agreements '
                      'where master_account = "{account_num}" '
                      'order by service_no'
                      .format(account_num=customer))
            services = c.fetchall()

            if not services:
                print("No services")
            else:
                for service in services:
                    print(service)

        else:
            print("Invalid Customer, Customer does not exist or is under another Manager")

        return 0

    # Create a new master account
    def createaccount(self):

        account_no = input("Enter the account number")
        customer_name = input("Enter the customer name")
        contact_info = input("Enter the customer contact info")
        customer_type = input("Enter the customer type")
        start_date = input("Enter the customer start date: YYYY-MM-DD")
        end_date = input("Enter the customer end date: YYYY-MM-DD")
        total_amount = input("Enter the total amount")

        print(account_no)

        c.execute("insert into accounts(account_no, account_mgr, customer_name, "
                  "contact_info, customer_type, start_date, end_date, total_amount)"
                  "values(?,?,?,?,?,?,?,?)",
                  (account_no, self.user_id, customer_name, contact_info, customer_type,
                   start_date, end_date, total_amount))

        print("Customer successfuly added\n")

        return 0

    # Ask the manager to produce a customer id, otherwise a customer name is too general
    def newserviceagreement(self):
        customer = input("Please enter a customer number")
        location = input("Please enter the location")
        waste_type = input("Please enter the waste type")
        pick_up_schedule = input("Please enter the pick up schedule")
        local_contact = input("Please enter the local contact")
        internal_cost = input("Please enter the internal cost (int)")
        price = input("Please enter the price (real)")

        c.execute("select service_no "
                  "from service_agreements ")

        service_numbers = c.fetchall()
        maximum_num = 0

        for num in service_numbers:
            if int(num[0]) >= maximum_num:
                maximum_num = int(num[0])

        maximum_num = maximum_num + 1
        # Insert information on the given customer
        c.execute("insert into service_agreements "
                  "values(?,?,?,?,?,?,?,?) ", (str(maximum_num), customer, location, waste_type, pick_up_schedule,
                                               local_contact, internal_cost, price))

        print('a')
        # Update the total_amount for the customer
        c.execute("select a.total_amount "
                  "from accounts a "
                  "where a.account_no = '{account}' "
                  .format(account=customer))
        total = c.fetchone()[0]

        c.execute("update accounts "
                  "set total_amount = '{new_total}' "
                  "where account_no = {account} "
                  .format(new_total=total+price, account=customer))

        print("Service agreement successfully created")

        return 0

    # Print out the summary report for a customer
    def summaryreport(self):
        customer_account = input("Enter the customer account number ")
        c.execute("select count(a.service_no), sum(a.price), sum(a.internal_cost), count(distinct a.waste_type) "
                  "from service_agreements a "
                  "where a.master_account = '{inputAccount}' "
                  .format(inputAccount=int(customer_account)))

        customer_summary = c.fetchall()

        print("The count of services: {services} \n"
              "The sum of prices: {prices} \n"
              "The sum of internal costs: {internal} \n"
              "The waste types: {waste} \n"
              .format(services=customer_summary[0][0], prices=customer_summary[0][1],
                      internal=customer_summary[0][2], waste=customer_summary[0][3]))

        return 0


# Supervisors use the system to query information about the accounts of account managers they supervise
class Supervisor(Personnel):

    def __init__(self, user_id, username, role):
        Personnel.__init__(self, user_id, username, role)

    def main(self):
        logout_role = False
        print("You are logged in as a Supervisor\n")

        while not logout_role:
            print("Enter a following command (By Number):")
            print("1: Create a customer account")
            print("2: Create a summary report for a customer")
            print("3: Create a summary report for all account managers under your supervision")
            command = input("4: To logout\n")

            try:
                if int(command) == 1:
                    self.createaccountsuper()
                    conn.commit()

                if int(command) == 2:
                    self.summaryreportcustomer()
                    conn.commit()

                if int(command) == 3:
                    self.summaryreportmanager()
                    conn.commit()

                if int(command) == 4:
                    logout_role = True

            except TypeError:
                print("Invalid command")

        return 0

    def createaccountsuper(self):
        c.execute('select account_managers.pid '
                  'from account_managers, personnel '
                  'where account_managers.pid = personnel.pid '
                  'and personnel.supervisor_pid = {user_id}'.format(user_id=self.user_id))

        # Get the list of managers under the supervisor's supervision
        mgrpid_list = c.fetchall()

        # Temporary value for mg_id
        # Check to see if the manager is under this supervisor

        print("Please select an account manager under your supervision")
        print(mgrpid_list)

        valid = False
        mg_id = input("Enter the manager Id")
        for manager in mgrpid_list:
            if mg_id in manager[0]:
                print("Valid manager")
                valid = True

        if not valid:
            print("INvalid Manager")
            return 0

        # Additional check to see if the account number is unique
        unique_account = False
        account_no = input("Enter the account number")
        while not unique_account:
            c.execute("select account_no "
                      "from accounts "
                      "where account_no = {account_num} "
                      .format(account_num=account_no))
            accounts = c.fetchone()
            if accounts:
                print("Account number is not unique")
                account_no = input("Enter the account number")
            else:
                unique_account = True

        customer_name = input('Enter customer name: ')
        contact_info = input('Enter contact information: ')
        customer_type = input('Enter customer type: ')
        start_date = input('Enter start date (YYYY-MM-DD): ')
        end_date = input('Enter end date (YYYY-MM-DD): ')
        total_amount = input('Enter total amount: ')

        c.execute("insert into accounts "
                  "values(?,?,?,?,?,?,?,?);",
                  (account_no, mg_id, customer_name, contact_info,
                   customer_type, start_date, end_date, total_amount))

        print("Customer Creation successful")
        return 0

    # Create summary report with info about the accoutn manager as well
    def summaryreportcustomer(self):
        # If the view already exists, we should drop it
        c.execute("drop view if exists Customer_Report")
        c.execute("create view Customer_Report as "
                  "select a.master_account, c.account_mgr, "
                  "count(a.service_no), sum(a.price), sum(a.internal_cost), count(distinct a.waste_type) "
                  "from service_agreements a, accounts c, account_managers d, personnel e "
                  "where a.master_account = c.account_no "
                  "and e.pid = d.pid "
                  "and e.supervisor_pid = '{inuser_id}' "
                  "group by a.master_account, c.account_mgr; "
                  .format(inuser_id=self.user_id))

        c.execute("select accounts.account_no, account_managers.pid "
                  "from accounts, account_managers, personnel "
                  "where accounts.account_mgr = account_managers.pid "
                  "and account_managers.pid = personnel.pid "
                  "and personnel.supervisor_pid = '{mg}'"
                  .format(mg=self.user_id))

        print("All available customers (Customer on Left and Account Manager of the Right)")
        customerandmanager = c.fetchall()
        print(customerandmanager)

        in_an = input('Enter account_no: ')
        c.execute("select * "
                  "from Customer_Report a "
                  "where a.master_account = {inputAccount} "
                  .format(inputAccount=int(in_an)))

        # If the tuple is empty, the customer doesnt exist or cannot be accessed
        sum_cus_list = c.fetchall()

        if sum_cus_list:
            for item in sum_cus_list:
                print(item) 
        else:
            print("Account number doesn't exist or is not managed by a manager under your supervision")

        return 0

    # Print out the summary for each account manager under the supervisor's supervision
    def summaryreportmanager(self):
        c.execute("select b.account_mgr, count(b.account_no), count(a.service_no), sum(a.price), sum(a.internal_cost) "
                  "from service_agreements a, accounts b, personnel c "
                  "where a.master_account = b.account_no "
                  "and b.account_mgr = c.pid "
                  "and c.supervisor_pid = '{inuser_id}' "
                  "group by b.account_mgr "
                  "order by (sum(a.price) - sum(a.internal_cost)); "
                  .format(inuser_id=self.user_id))

        sum_mgr_list = c.fetchall()
        for item in sum_mgr_list:
                print("account manager: {} count of accounts: {} count of services: {} sum of prices: {} "
                      "sum of internal costs: {}"
                      .format(item[0], item[1], item[2], item[3], item[4]))

        return 0


# Dispatchers use the system to create schedules
class Dispatcher(Personnel):

    def __init__(self, user_id, username, role):
        Personnel.__init__(self, user_id, username, role)

    def main(self):
        logout_role = False
        print("You are logged in as a Dispatcher")

        while not logout_role:
            print("Enter a following command (By Number): ")
            print("1: Create a new route/service fulfillment ")
            command = input("2: To Logout \n")


            if int(command) == 1:
                self.createservice()
                conn.commit()

            if int(command) == 2:
                logout_role = True



        return 0

    # Method to create a service
    # This method will call every other method in this class
    # Some method calls will not be bound to any variable as the value they return is insignificant
    def createservice(self):
        # Prompt the dispatcher to select a service agreement
        # As well as a date and an id for the driver
        service_number = input('Enter service_no: ')
        date = input("Enter the date of the service (YYYY-MM-DD) : ")
        self.displaydrivers()
        driver_id = input('Enter driver id: ')
        print("a")
        master_account = self.getmaster(service_number)

        truck_id = self.gettruck(driver_id)
        print("b")
        container_pick_up = self.getcontainer(service_number)
        container_drop_off = self.getcontainer_dropoff(service_number)
        self.insertinto(date, master_account, service_number, truck_id, driver_id, container_pick_up, container_drop_off)

        print("Service Fulfillment created sucessfully")

        return 0

    def insertinto(self, date, master_account, service_number, truck_id,
                   driver_id, container_pick_up, container_drop_off):

        c.execute("insert into service_fulfillments "
                  "values(?,?,?,?,?,?,?);",
                  (date, master_account, service_number, truck_id,
                   driver_id, container_pick_up, container_drop_off))

        return 0

    def displaydrivers(self):
        c.execute("select distinct pid "
                  "from drivers; ")

        drivers = c.fetchall()
        print("Available drivers: ")
        for driver in drivers:
            print(driver)

        return 0

    def displayservicenum(self, service_number):
        c.execute("select b.driver_id, b.truck_id, b.cid_drop_off , b.cid_pick_up "
                  "from service_agreements a, service_fulfillments b "
                  "where a.service_no = b.service_no "
                  "and a.service_no = '{inService_no}'; "
                  .format(inService_no=service_number))

        dis_list = c.fetchall()
        for item in dis_list:
            print(item)
            print('\n')

        return 0

    def getmaster(self, service_number):

        # Get the master account for a service agreement
        c.execute("select a.master_account "
                  "from service_agreements a "
                  "where a.service_no = {input_sesrvice};"
                  .format(input_sesrvice=service_number))
        master_account = c.fetchone()[0]
        return master_account

    # Get the truck id for a driver, depends on if they own a truck or not
    def gettruck(self, driver_id):

        # Check to see if the driver owns a truck
        c.execute("select a.owned_truck_id "
                  "from drivers a "
                  "where a.pid = {inputDriver};"
                  .format(inputDriver=driver_id))

        truck_id = c.fetchone()
        if not truck_id:
            print('This driver owns no truck.')
            truck_id = input('Enter truck ID: ')
            return truck_id
        else:
            truck_id = truck_id[0]
            return truck_id

    # Get the container to be picked up
    def getcontainer(self, service_no):

        # Get the most recent day that the container was dropped off on
        c.execute("select max(julianday(date_time)) "
                  "from service_agreements a, service_fulfillments b "
                  "where a.service_no = '{inserviceno}' "
                  "and a.service_no = b.service_no "
                  "and a.master_account = b.master_account;"
                  .format(inserviceno=service_no))

        last_date = c.fetchone()[0]
        # If there is no last date ie, we need to use a dummy container
        if not last_date:
            container = '0000'
            return container

        # We assume that the last container to be dropped off is the one we now need to pick up
        else:
            c.execute("select b.cid_drop_off "
                      "from service_agreements a, service_fulfillments b "
                      "where a.service_no = '{inserviceno}' "
                      "and a.service_no = b.service_no "
                      "and a.master_account = b.master_account "
                      "and b.date_time = '{date_time}';"
                      .format(inserviceno=service_no, date_time=last_date))
            container = c.fetchone()
            if not container:
                return '0000'
            else:
                return container[0]

    # Get an appropriate container to be dropped off
    def getcontainer_dropoff(self, service_no):

        # Get the waste type required for the job
        c.execute("select a.waste_type "
                  "from service_agreements a, service_fulfillments b "
                  "where a.service_no = b.service_no "
                  "and a.master_account = b.master_account "
                  "and a.service_no = '{inserviceno}';"
                  .format(inserviceno=service_no))
        waste_type = c.fetchone()[0]

        # Get all containers of the appropriate waste type
        # That are available as well
        # Containers have a record in being picked up at the location (date prior to now)
        # And should also not be scheduled to be dropped off
        c.execute("select lower(v.container_id) "
                  "from container_waste_types v "
                  "where v.waste_type = '{waste}' "
                  "and v.container_id in "
                  "(SELECT a.container_id AS [Container ID] "
                  "FROM containers a "
                  "WHERE (SELECT COUNT(b.cid_drop_off) "
                  "FROM service_fulfillments b "
                  "WHERE b.cid_drop_off = a.container_id) = 0 "
                  "OR((SELECT COUNT(b.cid_drop_off) "
                  "FROM service_fulfillments b "
                  "WHERE b.cid_drop_off = a.container_id) <= "
                  "(SELECT COUNT(b.cid_pick_up) "
                  "FROM service_fulfillments b "
                  "WHERE b.cid_pick_up= a.container_id))); "
                  .format(waste=waste_type))

        containers = c.fetchall()
        print(waste_type)
        print(containers)

        container_available = False
        while not container_available:
            container_selected = input("Please select a container")
            for container in containers:
                if container_selected.lower() in container:
                    return container_selected
            else:
                print("Container not available, it is scheduled to be picked up or dropped off on a later date")

        return 0


# Drivers use the system to find out about their own schedule
class Driver(Personnel):

    def __init__(self, user_id, username, role):
        Personnel.__init__(self, user_id, username, role)

    def main(self):
        logout_role = False
        print("You are logged in as a Driver")

        while not logout_role:
            print("Enter a following command (By Number): ")
            print("1: List the tours you have been assigned to")
            command = input("2: To Logout\n")

            try:
                if int(command) == 1:
                    self.gettour()
                    conn.commit()

                if int(command) == 2:
                    logout_role = True

            except TypeError:
                print("Type Error Invalid command")

        return 0

    # Method used to get the info for a tour between two dates
    def gettour(self):
        print("To search for only one day, the one day before the desired date as the start date\n"
              "and enter one day after the desired date as the end date")
        lower = input('Enter the start date (YYYY-MM-DD): ')
        upper = input('Enter the end date (YYYY-MM-DD): ')
        print('\n')

        c.execute("select b.location, b.local_contact, b.waste_type, a.cid_drop_off, a.cid_pick_up "
                  "from service_fulfillments a, service_agreements b "
                  "where julianday(a.date_time) >= julianday('{lowerindate}') "
                  "and julianday(a.date_time) <= julianday('{upperindate}') "
                  "and a.driver_id = '{inputDriver}' "
                  "and a.service_no = b.service_no "
                  "and a.master_account = b.master_account;"
                  .format(lowerindate=lower, upperindate=upper, inputDriver=self.user_id))
        tour_list = c.fetchall()
        if not tour_list:
                print('Empty tour list')
                print('\n')
        else:
            for tour in tour_list:
                print('location: {}'.format(tour[0]))
                print('local contact: {}'.format(tour[1]))
                print('waste type: {}'.format(tour[2]))
                print('container drop off: {}'.format(tour[3]))
                print('container pick up: {}\n'.format(tour[4]))

        return 0


# Admins can enter users with login, role and password
class Admin:

    def main(self):
        logout_role = False
        print("You are logged in as an Admin")

        while not logout_role:
            command = input("Enter a following command (By Number): \n"
                            "1: Create a new user \n"
                            "2: To logout of the administrator account \n")

            if int(command) == 1:
                user_id = int(self.createuserid())
                role = self.getrole()
                if role == -1:
                    return 0
                login_username = self.get_username()
                password = self.getpassword()
                AdminControls.adduser(user_id, role, login_username, password)
                print("New user successfully created")

            if int(command) == 2:
                logout_role = True

        return 0

    # Check if the username is already in the database, returns False if it exists
    def usernameunique(self, username):
        c.execute("select * from users where login = '{login_username}'".format(login_username=username))
        id_exists = c.fetchone()
        if id_exists:
            return False
        else:
            return True

    def createuserid(self):
        c.execute('select user_id from users')
        user_id = c.fetchall()
        new_user = 0

        for id in user_id:
            if int(id[0]) >= new_user:
                new_user = int(id[0])

        return int(new_user) + 1

    def getrole(self):
        roles = ('driver', 'account manager', 'dispatcher', 'supervisor')
        role_incorrect = True
        while role_incorrect:
            role = input("Enter the role of the user (account manager, supervisor, dispatcher, driver)")
            if str(role) not in roles:
                print("Error, the role is an illegal value")
            else:
                return role

    def get_username(self):
        login_username = ''
        login_exists = True
        while login_exists:
            login_username = input("Enter a user name")
            if self.usernameunique(login_username):
                login_exists = False
            else:
                print("The username already exists")

        return login_username

    def getpassword(self):
        password = ''
        incorrect_password = True
        # A confirmation to the password
        while incorrect_password:
            password = input("Enter a password")
            password2 = input("Please reconfirm your password")
            if password == password2:
                incorrect_password = False

        return password

# ----------------------------End of class declarations----------------------------


def main():
    exit_program = False

    while not exit_program:

        print("Welcome to the main menu \n"
              "Enter a following command (By Number) \n")
        user = input("1: To enter as a user \n"
                     "2: To enter as an administrator \n"
                     "3: To quit and exit the program\n")

        user = user.replace(" ", "")

        try:

            if int(user) == 3:
                exit_program = True

            if int(user) == 2:
                admin = Admin()
                admin.main()

            if int(user) == 1:
                user_name = input("Please enter your username")
                if login(user_name):
                    role = get_role(user_name)[0]
                    user_id = get_id(user_name)

                    if role.lower() == "account manager":
                        accountmanager = AccountManager(user_id, user_name, role)
                        accountmanager.main()

                    if role.lower() == "supervisor":
                        supervisor = Supervisor(user_id, user_name, role)
                        supervisor.main()

                    if role.lower() == "dispatcher":
                        dispatcher = Dispatcher(user_id, user_name, role)
                        dispatcher.main()

                    if role.lower() == "driver":
                        driver = Driver(user_id, user_name, role)
                        driver.main()

        except TypeError:
            print("Unknown Command")

        except ValueError:
            print("Unknown Value")

    # Commit changes to the db and close the connection
    conn.commit()
    conn.close()
    return 0


main()
