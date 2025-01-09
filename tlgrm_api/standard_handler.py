# standard_handler.py

from telebot import TeleBot
from telebot.types import Message
from peewee import IntegrityError

from setting import TOKEN_TLG
from database.models import db, UserTelegram
from database.core import crud

bot = TeleBot(TOKEN_TLG)

store_func = crud.create()

# словарь для сохранения данных о пользователе перед передачей в таблицы
data_user = dict()

def _start(message: Message) -> None:
    data_user['user_id'] = message.from_user.id
    data_user['username'] = message.from_user.username or 'Unknown'
    data_user['first_name'] = message.from_user.first_name or 'Unknown'
    data_user['last_name'] = message.from_user.last_name or 'Unknown'
    try:
        store_func(db, UserTelegram, *[data_user])
        bot.send_message(message.chat.id,'Добро пожаловать, <b>{0.first_name}</b>!\nЯ, '
                                         '<b>{1.first_name}</b>, бот созданный, чтобы Вы '
                                         'могли со мной общаться. 🙂\nЯ помогу вам найти '
                                         'авиабилеты на нужное Вам направление, а заодно '
                                         'сделаю прогноз погоды в месте Вашего назначения,'
                                         ' на пять дней вперёд. Удачи!'
                                         .format(message.from_user, bot.get_me()),
                                         parse_mode="html")
        bot.send_message(message.chat.id, 'Подсказка, команда: <b>/help</b>', parse_mode="html")
    except IntegrityError as exp:
        print(str(exp))
        bot.reply_to(message, f'Рад вас снова видеть, {data_user["first_name"]}!')


# функция подсказка, рассказывает какими
# командами пользователь может воспользоваться
# в этом боте
def _help(message: Message) -> None:
    bot.send_message(message.chat.id,
                     'В этом боте можно воспользоваться следующими '
                     'командами:\n  <b>/start</b>,   <b>/help</b>'
                     ',   <b>/low</b>,   <b>/high</b>,\n  <b>/custom</b>,'
                     '  <b>/history</b>.\nЕсли Вы введете слово, бот '
                     'ответит Вам эхом, если это слово не "привет". 🙂',
                     parse_mode='html')


class StandardHandler:
    @staticmethod
    def start():
        return _start

    @staticmethod
    def help():
        return _help

