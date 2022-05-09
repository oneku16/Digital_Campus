
from datetime import datetime
import time
import serial
import MySQLdb
import serial

# establish connection to MySQL. You'll have to change this for your database.
dbConn = MySQLdb.connect("localhost", "root", "1", "db_bikes") or die(
    "could not connect to database")
# open a cursor to the database
cursor = dbConn.cursor()

device = 'COM3'  # this will have to be changed to the serial port you are using
try:
    print("Trying...", device)
    arduino = serial.Serial(device, 9600)
except:
    print("Failed to connect on", device)


while True:
    time.sleep(1)
    try:
        result = 0
        currentUser = ''
        data = arduino.readline()
        res = str(data)[2:9]
        try:
            cursor = dbConn.cursor()

            cursor.execute(
                f"SELECT * FROM bike_monitor where user_id = \"{res}\"")
            userExsist = cursor.fetchall()

            if not userExsist:
                command = "200"
                arduino.write(command.encode())
                now = datetime.now()
                current_time = now.strftime("%H:%M")
                cursor.execute(
                    f"UPDATE bike_monitor SET user_id = \"{res}\", take = \"{current_time}\", reserved = '0',status = '0' where status = '1' limit 1")
                print("User ", res, " was added")
            else:
                command = "0"
                arduino.write(command.encode())
                cursor.execute(
                    f"SELECT * FROM bike_monitor where user_id = \"{res}\" and reserved = '0'")
                reserved = cursor.fetchall()
                print(reserved)
                if res == reserved[0][1]:
                    if reserved[0][3] == reserved[0][4]:
                        cursor.execute(
                            f"UPDATE bike_monitor SET user_id = '', take = '', reserved='1', status = '1' where user_id = \"{res}\"")
                        print("User ", res, " was cleaned")

                    else:
                        cursor.execute(
                            f"UPDATE bike_monitor SET status = '0' where user_id = \"{res}\" ")
                        print("Status was changed")
            dbConn.commit()
            cursor.close()
        except MySQLdb.IntegrityError:
            print("failed to insert data")
        finally:
            cursor.close()
    except:
        print("Processing")
