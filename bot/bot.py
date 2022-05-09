from traceback import print_tb
import telebot
from telebot import types
import MySQLdb
from datetime import datetime
from telebot.types import ReplyKeyboardRemove


# DB & Bot connection
db = MySQLdb.connect("localhost", "root", "1", "db_bikes") or die(
    "could not connect to database")
bot = telebot.TeleBot('5304555854:AAEuWKOhEklQASHjkG7oU0F8AV4jwukkk5Q')


# dependencies
show_bike = ''
free_bike = ()
NAME = []


# Start command
@bot.message_handler(commands=['start'])
def start_message(message):
    global NAME
    bot.send_message(message.chat.id, 'Welcome, please Enter your name')
    NAME = []


# Show all bikes
@bot.message_handler(content_types='text')
def message_reply(message):
    global show_bike
    free_bike = ()

    NAME.append(message.text)

    if len(NAME) > 0:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Show Bikes")
        markup.add(item1)
        bot.send_message(message.chat.id, 'Select an option',
                         reply_markup=markup)

        if message.text == "Show Bikes":
            cursor = db.cursor()
            cursor.execute(
                "SELECT * FROM bike_monitor")
            bike_list = cursor.fetchall()
            db.commit()

            # Printing list of bikes
            for bike in bike_list:
                if bike[4] == 0 or bike[3] == 0:
                    show_bike += ">> Bike #" + \
                        str(bike[0]) + " taken at: " + str(bike[2]) + "\n\n"
                else:
                    show_bike += (">> Bike #" +
                                  str(bike[0]) + " is free") + "\n\n"
                    free_bike = (bike,) + (free_bike)

            bot.send_message(message.chat.id, show_bike,
                             parse_mode='Markdown')

            # Adding buttons
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for bike in free_bike:
                markup.add(types.KeyboardButton(
                    "bike #" + str(bike[0])))
            bot.send_message(
                message.chat.id, 'Please, select a bike', reply_markup=markup)

            # cleaning bike list
            show_bike = ''

        # Selecting bike
        elif message.text[:4] == "bike":

            cursor = db.cursor()

            # take user_id
            cursor.execute(
                "SELECT card_id FROM users where name = '%s'" % NAME[0])
            user_list = cursor.fetchall()
            user_id = str(user_list[0][0])

            # take bike info about user
            cursor.execute(
                f"SELECT * FROM bike_monitor where user_id = \"{user_id}\"")
            userExsist = cursor.fetchall()
            if not userExsist:
                bot.send_message(
                    message.chat.id, 'Please, enter your name', reply_markup=ReplyKeyboardRemove())

                now = datetime.now()
                current_time = now.strftime("%H:%M")
                cursor.execute(
                    f"UPDATE bike_monitor SET user_id = \"{user_id}\", take = \"{current_time}\", reserved = '0' where reserved = '1' and id = \"{message.text[6:]}\" limit 1")
                print("User ", user_id, " was added")
                bot.send_message(
                    message.chat.id, 'You have reserved bike #'+str(message.text[6:]))
            else:
                bot.send_message(
                    message.chat.id, 'You have already reserved bike')
            db.commit()

    print(NAME)


bot.infinity_polling()
