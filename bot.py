import telebot
import time
import datetime
import calendar
import database


class Bot:
    def __init__(self):
        self.bot = telebot.TeleBot('1280237155:AAF4Blri2FajDY6fcPzkkqYnX2w8Lrbsvuo')
        self.db = database.Database()
        self.buffer_lesson = ['0', '0', '0']

        @self.bot.message_handler(commands=['start'])
        def start_message(message: telebot.types.Message):
            keyboard = telebot.types.InlineKeyboardMarkup()
            key_reg = telebot.types.InlineKeyboardButton(text='Зарегистрироваться', callback_data='reg')
            keyboard.add(key_reg)
            self.bot.send_message(message.chat.id, 'Привет! Еще не зарегистрирован? Регистрируйся скорее!',
                                  reply_markup=keyboard)

        @self.bot.message_handler(content_types=['text'])
        def process(message: telebot.types.Message):
            greetings = ['привет', 'доброе утро', 'добрый день', 'добрый вечер',
                         'доброй ночи', 'здравствуй', 'привет)', 'привет!']
            goodbye = ['пока', 'до встречи', 'до свидания']
            if message.text.lower() in greetings:
                self.bot.send_message(message.chat.id, 'Доброе утро! Время начинать учиться! Напиши \'меню\' '
                                                       'и распланируй свой день.')
            elif message.text.lower() in goodbye:
                self.bot.send_message(message.chat.id, 'До скорой встречи! Приходи еще:з')
            elif message.text.lower() == 'меню':
                print_menu(message)
            else:
                self.bot.send_message(message.chat.id, 'Просто напиши \'меню\', и я покажу, что умею~')

        def print_menu(message: telebot.types.Message):
            keyboard = telebot.types.InlineKeyboardMarkup()
            key_check = telebot.types.InlineKeyboardButton(text='Посмотреть расписание на сегодня',
                                                           callback_data='check')
            key_plans = telebot.types.InlineKeyboardButton(text='Посмотреть план на день', callback_data='plans')
            key_add = telebot.types.InlineKeyboardButton(text='Добавить пару в расписание', callback_data='add')
            key_action = telebot.types.InlineKeyboardButton(text='Составить список дел',
                                                            callback_data='action')
            keyboard.add(key_check)
            keyboard.add(key_plans)
            keyboard.add(key_add)
            keyboard.add(key_action)
            self.bot.send_message(message.chat.id, text='Что ты хочешь сделать?',
                                  reply_markup=keyboard)

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_worker(call):
            if call.data == 'reg':
                self.register(call.message, call.from_user.id)
            elif call.data == 'check':
                self.print_timetable(call.message, call.from_user.id)
            elif call.data == 'plans':
                self.print_plan(call.message, call.from_user.id)
            elif call.data == 'add':
                self.add_lesson(call.message)
            elif call.data == 'action':
                self.bot.send_message(call.message.chat.id, 'Хорошо. Составь свой список дел. Напиши все свои дела, '
                                                            'каждое отдельным сообщением, а когда закончишь, напиши '
                                                            '\'все\', чтобы я понял, что список закончен:з')
                self.add_action(call.message, call.from_user.id)

    def register(self, message: telebot.types.Message, person_id):
        if person_id in self.db.get_users():
            self.bot.send_message(person_id, "Ты ведь уже зарегистрирован!\n")
        else:
            self.bot.send_message(person_id, "Приятно познакомиться:з")
            self.db.add_user(person_id)

    def print_timetable(self, message: telebot.types.Message, person_id):
        data = database.get_data(person_id, 'timetable')
        now_date = datetime.datetime.now()
        now_weekday = calendar.day_name[now_date.weekday()]
        if now_weekday.lower() != 'sunday':
            self.bot.send_message(message.chat.id, 'Расписание на сегодня:')
        else:
            self.bot.send_message(message.chat.id, 'Сегодня нет занятий!')

        for elem in data:
            if elem[0] == now_weekday:
                self.bot.send_message(message.chat.id, 'Предмет: ' + elem[1] + ', время: ' + elem[2] + ';')

    def print_plan(self, message: telebot.types.Message, person_id):
        data = database.get_data(person_id, 'plan')
        if len(data) != 0:
            self.bot.send_message(message.from_user.id, 'Список дел на сегодня:\n' + '\n'.join(data))
        else:
            self.bot.send_message(message.chat.id, 'Кажется, ты еще не составил свой список дел! Напиши слово'
                                                   ' \'меню\', и сможешь его создать!')

    def add_lesson(self, message: telebot.types.Message):
        self.bot.send_message(message.from_user.id, 'Введи название предмета: ')
        self.bot.register_next_step_handler(message, self.add_weekday(message))

    def add_weekday(self, message: telebot.types.Message):
        self.buffer_lesson[1] = message.text
        self.bot.send_message(message.chat.id, 'Введи день недели, в который он проходит: ')
        self.bot.register_next_step_handler(message, self.add_time(message))

    def add_time(self, message: telebot.types.Message):
        if message.text.lower() == 'понедельник':
            self.buffer_lesson[0] = 'Monday'
        elif message.text.lower() == 'вторник':
            self.buffer_lesson[0] = 'Tuesday'
        elif message.text.lower() == 'среда':
            self.buffer_lesson[0] = 'Wednesday'
        elif message.text.lower() == 'четверг':
            self.buffer_lesson[0] = 'Thursday'
        elif message.text.lower() == 'пятница':
            self.buffer_lesson[0] = 'Friday'
        elif message.text.lower() == 'суббота':
            self.buffer_lesson[0] = 'Saturday'

        self.bot.send_message(message.chat.id, 'Введи время: ')
        self.bot.register_next_step_handler(message, self.new_lesson(message))

    def new_lesson(self, message: telebot.types.Message):
        self.buffer_lesson[2] = message.text
        database.add_data(message.chat.id, 'timetable', ' '.join(self.buffer_lesson))
        self.bot.send_message(message.chat.id, 'Готово! Вписал новое занятие в расписание:)')

    def add_action(self, message: telebot.types.Message, person_id):
        if isinstance(message.text, str):
            if message.text.lower() == 'все':
                self.bot.send_message(message.from_user.id, 'Замечательно, все внесено в план! '
                                                            'Ты всегда можешь посмотреть свой список дел,'
                                                            ' просто написав мне \'меню\' и нажав на кнопку '
                                                            '\'Посмотреть план на день\'')
            else:
                database.add_data(person_id, 'plan', message.text)
                self.bot.send_message(message.from_user.id, "Что-то еще?")
                self.bot.register_next_step_handler(message, self.add_action)
        else:
            self.bot.send_message(message.from_user.id, "Давай лучше текстом, хорошо?")
            self.bot.register_next_step_handler(message, self.add_action)

    def plan(self):
        self.bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    bot = Bot()
    while True:
        try:
            bot.plan()
        except:
            time.sleep(5)
