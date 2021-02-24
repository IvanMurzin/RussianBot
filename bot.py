import random
import telebot
import time
from values import *

bot = telebot.TeleBot(API_KEY)


class User:
    position_endings = 0
    position_stress = 0
    answer_endings = 0
    answer_stress = 0
    endings = []
    stress = []
    all_endings = 0
    all_stress = 0
    mistakes_endings = []
    mistakes_stress = []


def get_random_array(a):
    result = []
    for _ in range(len(a)):
        r = random.choice(a)
        while r in result:
            r = random.choice(a)
        result.append(r)
    return result


def ask_endings(id, user):
    # get the right and wrong answer
    key = user.endings[user.position_endings]
    value = endings_dict[key]
    # send question to the user
    if random.getrandbits(1):
        bot.send_message(id, key + " или " + value + " ?")
        # save correct answer
        user.answer_endings = 1
    else:
        bot.send_message(id, value + " или " + key + " ?")
        # save correct answer
        user.answer_endings = 2
    # save user information in the dict
    storage[id] = user


def ask_stress(id, user):
    # get the right and wrong answer
    key = user.stress[user.position_stress]
    value = stress_dict[key]
    # send question to the user
    bot.send_message(id, "На какую букву падает ударение в слове\n" + key + "?")
    # save correct answer
    user.answer_stress = value
    # save user information in the dict
    storage[id] = user


def start_endings(id):
    # sending hint about endings
    bot.send_message(id, hint_endings)
    # get or create User class
    user = storage.get(id, User())
    # set cursor of array
    user.position_endings = 0
    # generate random array of endings
    keys = list(endings_dict.keys())
    user.endings = get_random_array(keys)
    ask_endings(id, user)


def start_stress_in_a_word(id):
    # sending hint stress
    bot.send_message(id, hint_stress)
    # get or create User class
    user = storage.get(id, User())
    # set cursor of array
    user.position_stress = 0
    # generate random array of stress
    keys = list(stress_dict.keys())
    user.stress = get_random_array(keys)
    ask_stress(id, user)


def get_message_from_user(id, message):
    # get or create User class
    user = storage.get(id, User())
    # if checking endings
    if user.endings:
        # another user input
        if message != "1" and message != "2":
            bot.send_message(id, "Для выхода из режима проверки введите /exit")
            return
        # move endings cursor
        user.position_endings += 1
        # collecting statistics
        user.all_endings += 1
        # correct answer
        if message == str(user.answer_endings):
            bot.send_message(id, "Правильно")
        # wrong answer
        else:
            bot.send_message(id, "Неправильно")
            bot.send_message(id, "Правильно:\n" + user.endings[user.position_endings - 1])
            # remember wrong answer
            user.mistakes_endings.append(user.endings[user.position_endings - 1])
        # if we at the end of the list exit checking
        if user.position_endings == len(user.endings):
            bot.send_message(id, "Вы проверили все, что было.")
            user.endings = []
            return
        ask_endings(id, user)

    # if checking stress
    elif user.stress:
        # another user input
        if not message.isnumeric():
            bot.send_message(id, "Для выхода из режима проверки введите /exit")
            return
        # move stress cursor
        user.position_stress += 1
        # collecting statistics
        user.all_stress += 1
        # correct answer
        if message == user.answer_stress:
            bot.send_message(id, "Правильно")
        # wrong answer
        else:
            bot.send_message(id, "Неправильно")
            # remember wrong answer
            answer = user.stress[user.position_stress - 1]
            position = int(user.answer_stress) - 1
            correct = "".join([answer[:position] + answer[position].upper() + answer[position + 1:]])
            if answer == "досыта":
                correct = "дОсЫта"
            if answer == "одновременно":
                correct = "одноврЕмЕнно"
            if answer == "ржаветь":
                correct = "ржАвЕть"
            bot.send_message(id, "Правильно:\n" + correct)
            user.mistakes_stress.append(correct)
        # if we at the end of the list exit checking
        if user.position_stress == len(user.stress):
            bot.send_message(id, "Вы проверили все, что было.")
            user.stress = []
            return
        ask_stress(id, user)

    # if there is no checking
    else:
        bot.send_message(id, "Кажется, я такого не знаю")


def show_statistics(id):
    # safely getting User
    user = storage.get(id, User())
    endings_message = \
        "Всего окончаний проверено: " + str(user.all_endings) + "\nВсего ошибок в окончаниях: " + str(
            len(user.mistakes_endings))
    bot.send_message(id, endings_message)
    stress_message = \
        "Всего ударений проверено: " + str(user.all_stress) + "\nВсего ошибок в ударениях: " + str(
            len(user.mistakes_stress))
    bot.send_message(id, stress_message)


def show_mistakes(id):
    # safely getting User
    user = storage.get(id, User())
    endings_message = "Ошибки в окончаниях:\n" + "\n".join(user.mistakes_endings)
    bot.send_message(id, endings_message)
    stress_message = "Ошибки в ударениях:\n" + "\n".join(user.mistakes_stress)
    bot.send_message(id, stress_message)


def clear(id):
    user = storage.get(id, User())
    user.position_endings = 0
    user.position_stress = 0
    user.answer_endings = 0
    user.answer_stress = 0
    user.endings = []
    user.stress = []
    user.all_endings = 0
    user.all_stress = 0
    user.mistakes_endings = []
    user.mistakes_stress = []


if __name__ == '__main__':
    while 1:
        try:
            @bot.message_handler(commands=['start', 'help'])
            def send_help(message):
                # send help message
                bot.send_message(message.from_user.id, help_message)


            @bot.message_handler(commands=['endings'])
            def command_endings(message):
                # safely getting User
                user = storage.get(message.from_user.id, User())
                if user.endings or user.stress:
                    bot.send_message(message.from_user.id, "Уже идет проверка знаний.")
                    return
                start_endings(message.from_user.id)


            @bot.message_handler(commands=['stress_in_a_word'])
            def command_stress_in_a_word(message):
                # safely getting User
                user = storage.get(message.from_user.id, User())
                if user.endings or user.stress:
                    bot.send_message(message.from_user.id, "Уже идет проверка знаний.")
                    return
                start_stress_in_a_word(message.from_user.id)


            @bot.message_handler(commands=['exit'])
            def command_exit(message):
                # safely getting User
                user = storage.get(message.from_user.id, User())
                if not (user.endings or user.stress):
                    # send help message
                    bot.send_message(message.from_user.id, help_message)
                    return
                user.endings = []
                user.stress = []
                bot.send_message(message.from_user.id, "Всего доброго")
                # send help message
                bot.send_message(message.from_user.id, help_message)


            @bot.message_handler(commands=['statistics'])
            def command_statistics(message):
                show_statistics(message.from_user.id)


            @bot.message_handler(commands=['mistakes'])
            def command_mistakes(message):
                show_mistakes(message.from_user.id)


            @bot.message_handler(commands=['clear'])
            def command_clear(message):
                clear(message.from_user.id)
                bot.send_message(message.from_user.id, "Все чисто")


            @bot.message_handler(content_types=['text'])
            def get_text_messages(message):
                get_message_from_user(message.from_user.id, message.text)


            bot.polling(none_stop=True)
        except:
            print("Crashed again")
        time.sleep(1)
