# main.py
# имя бота t.me/Training_frst_Bot

from telebot.types import BotCommand, Message
from telebot.custom_filters import StateFilter
from telebot import TeleBot, types
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup
from typing import Dict, Any, List
from random import choice as choice
from datetime import datetime, timezone
from peewee import IntegrityError

from database.core import crud
from site_api.core import site_api
from setting import TOKEN_TLG, TOKEN_TRVL, DEFAULT_COMMANDS, DATE_FORMAT, hello_lst
from database.models import db, UserTelegram, History
from site_api.owm_api import WeatherInterface
from tlgrm_api.standard_handler import StandardHandler

state_storage = StateMemoryStorage()

bot = TeleBot(TOKEN_TLG, state_storage=state_storage)

stndrd_hndlr = StandardHandler()
weather_api = WeatherInterface()


class UserState(StatesGroup):
    """
    Класс состояний
    """
    DEPARTURE_LOW = State()
    DESTINATION_LOW = State()
    DATE_DEPARTURE_LOW = State()
    DEPARTURE_HIGH = State()
    DESTINATION_HIGH = State()
    DATE_DEPARTURE_HIGH = State()
    DEPARTURE_CUSTOM = State()
    DESTINATION_CUSTOM = State()
    DATE_DEPARTURE_CUSTOM = State()
    AWAITING_MIN_COST = State()
    AWAITING_MAX_COST = State()
    AWAITING_DIRECT_TRIP = State()


# словарь для сохранения данных истории
data_hist = dict()
data_user = dict()

# Добавляем фильтр состояния
bot.add_custom_filter(StateFilter(bot))

# объявление функций из других модулей
store_func = crud.create()
fact_tickets = site_api.get_tickets_trvl()
fact_by_IATA = site_api.get_date_IATA()
weather_forecast = weather_api.weather_forecast()

# Устанавливаем команды бота
bot.set_my_commands([BotCommand(*cmd) for cmd in DEFAULT_COMMANDS])

# Обработчик команды /start
bot.message_handler(commands=['start'])(stndrd_hndlr.start())

# Обработчик команды /help
bot.message_handler(commands=['help'])(stndrd_hndlr.help())


# обработчик команды /low
# здесь пользователь может посмотреть
# стоимость пяти самых дешевых авиабилетов
# на конкретное направление
@bot.message_handler(commands=['low'], state="*")
def low_handler(message: Message) -> None:
    user_id = message.from_user.id
    if UserTelegram.get_or_none(UserTelegram.user_id == user_id) is None:
        bot.reply_to(message, "Вы не зарегистрированы. Напишите /start")
        return
    bot.send_message(message.chat.id, 'Вы находитесь на треке поиска дешевых '
                                      'билетов на выбранное Вами направление.')
    bot.send_message(message.chat.id, 'Введите пункт отправления на русском языке:')
    bot.set_state(message.from_user.id, UserState.DEPARTURE_LOW, message.chat.id)


@bot.message_handler(state=UserState.DEPARTURE_LOW)
def handler_departure(message: Message) -> None:
    handle_departure(message, UserState.DESTINATION_LOW)


@bot.message_handler(state=UserState.DESTINATION_LOW)
def handler_destination(message: Message) -> None:
    handle_destination(message, UserState.DATE_DEPARTURE_LOW)


@bot.message_handler(state=UserState.DATE_DEPARTURE_LOW)
def handler_date_departure(message: Message) -> None:
    date_departure = message.text.replace(' ', '')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['date_departure'] = date_departure
    res_kod_iata = looking_route(message, data)
    if not res_kod_iata:
        bot.send_message(message.chat.id,
                         'Введены не правильные, пункт '
                         'отправления  или пункт прибытия.\n'
                         'Выберите команду <b>/low</b> снова'
                         ' и повторите ввод.',
                         parse_mode='html')
    else:
        bot.send_message(message.chat.id, 'Всё Ok. полетели!')
        aeroport_origin = res_kod_iata['origin']['iata']
        aeroport_destination = res_kod_iata['destination']['iata']
        url_tickets = (f'https://api.travelpayouts.com/aviasales/'
                       f'v3/prices_for_dates?origin={aeroport_origin}'
                       f'&destination={aeroport_destination}'
                       f'&departure_at={data['date_departure']}&unique=false&sorting=price&'
                       f'direct=false&currency=rub&limit=5&token={TOKEN_TRVL}')
        try:
            result = fact_tickets('GET', url_tickets, params=None).json()
            if len(result['data']) > 0:
                data_hist_1 = scr_result(result, message, res_kod_iata, '/low', message.from_user.id)
                # запрашиваем прогноз погоды на пять дней
                weather_data = weather_forecast(data['destination'])
                scr_weather(message, weather_data, data['destination'])
                try:
                    store_func(db, History, *[data_hist_1])
                except IntegrityError:
                    bot.send_message(message.chat.id,
                                     'Что-то пошло не так, '
                                     'при изменении таблицы History')
            else:
                bot.send_message(message.chat.id,
                                 'Что-то пошло не так, '
                                 'не нашел билетов на данное направление.')
        except AttributeError:
            bot.send_message(message.chat.id,
                             'Введена не правильная, дата'
                             ' отправления.\nВыберите команду'
                             ' <b>/low</b> снова и повторите'
                             ' ввод.',
                             parse_mode='html')
    bot.delete_state(message.from_user.id, message.chat.id)


# Обработчик команды /high
@bot.message_handler(commands=['high'], state="*")
# обработчик команды /high
# здесь пользователь может посмотреть
# стоимость пяти самых дешевых авиабилетов
# на конкретное направление
def high_handler(message: Message) -> None:
    user_id = message.from_user.id
    if UserTelegram.get_or_none(UserTelegram.user_id == user_id) is None:
        bot.reply_to(message, "Вы не зарегистрированы. Напишите /start")
        return
    bot.send_message(message.chat.id, 'Вы находитесь на треке поиска дорогих '
                                      'билетов на выбранное Вами направление.')
    bot.send_message(message.chat.id, "Введите пункт отправления на русском языке:")
    bot.set_state(message.from_user.id, UserState.DEPARTURE_HIGH, message.chat.id)


@bot.message_handler(state=UserState.DEPARTURE_HIGH)
def handler_departure_high(message: Message) -> None:
    handle_departure(message, UserState.DESTINATION_HIGH)


@bot.message_handler(state=UserState.DESTINATION_HIGH)
def handler_destination_high(message: Message) -> None:
    handle_destination(message, UserState.DATE_DEPARTURE_HIGH)


@bot.message_handler(state=UserState.DATE_DEPARTURE_HIGH)
def handler_date_departure_high(message: Message) -> None:
    date_departure = message.text.replace(' ', '')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['date_departure'] = date_departure
    res_kod_iata = looking_route(message, data)
    if not res_kod_iata:
        bot.send_message(message.chat.id,
                         'Введены не правильные, пункт'
                         ' отправления или пункт прибытия.\n'
                         'Выберите команду <b>/high</b> снова'
                         ' и повторите ввод.',
                         parse_mode='html')
    else:
        bot.send_message(message.chat.id, 'Всё Ok. полетели!')
        aeroport_origin = res_kod_iata['origin']['iata']
        aeroport_destination = res_kod_iata['destination']['iata']
        url_tickets = (f'https://api.travelpayouts.com/aviasales/'
                       f'v3/prices_for_dates?origin={aeroport_origin}'
                       f'&destination={aeroport_destination}'
                       f'&departure_at={date_departure}&unique=false&sorting=price&'
                       f'direct=false&currency=rub&limit=30&token={TOKEN_TRVL}')
        try:
            result = fact_tickets('GET', url_tickets, params=None).json()
            if len(result['data']) > 0:
                sort_result = list(sorted(result['data'], key=lambda elem: elem['price'], reverse=True))
                # Получаем первые пять элементов, если они есть
                # Или возвращаем все элементы, если их меньше пяти
                sort_five = sort_result[:5] if len(sort_result) >= 5 else sort_result
                result['data'] = sort_five
                data_hist_2 = scr_result(result, message, res_kod_iata, '/high', message.from_user.id)
                # запрашиваем прогноз погоды на пять дней
                weather_data = weather_forecast(data['destination'])
                scr_weather(message, weather_data, data['destination'])
                try:
                    store_func(db, History, *[data_hist_2])
                except IntegrityError:
                    bot.send_message(message.chat.id,
                                     'Что-то пошло не так, '
                                     'при изменении таблицы History')
            else:
                bot.send_message(message.chat.id,
                                 'Что-то пошло не так, '
                                 'не нашел билетов на данное направление.')
        except AttributeError:
            bot.send_message(message.chat.id,
                             'Введена не правильная, дата'
                             ' отправления.\nВыберите команду'
                             ' <b>/high</b> снова и повторите'
                             ' ввод.',
                             parse_mode='html')
    bot.delete_state(message.from_user.id, message.chat.id)


# обработчик команды /custom
# здесь пользователь может посмотреть
# стоимость пяти самых дешевых авиабилетов
# на конкретное направление
@bot.message_handler(commands=['custom'], state="*")
def handle_custom(message):
    user_id = message.from_user.id
    if UserTelegram.get_or_none(UserTelegram.user_id == user_id) is None:
        bot.reply_to(message, 'Вы не зарегистрированы. Напишите /start')
        return
    bot.send_message(message.chat.id,
                     'Вы находитесь на треке поиска билетов по выбранным Вами'
                     'параметрам на выбранное направление.')
    bot.send_message(message.chat.id,
                     'Введите пункт отправления на русском языке:')
    bot.set_state(message.from_user.id, UserState.DEPARTURE_CUSTOM)


@bot.message_handler(state=UserState.DEPARTURE_CUSTOM)
def handler_departure_custom(message: Message) -> None:
    handle_departure(message, UserState.DESTINATION_CUSTOM)


@bot.message_handler(state=UserState.DESTINATION_CUSTOM)
def handler_destination_custom(message: Message) -> None:
    handle_destination(message, UserState.DATE_DEPARTURE_CUSTOM)


@bot.message_handler(state=UserState.DATE_DEPARTURE_CUSTOM)
def handler_direct_custom(message: Message) -> None:
    date_departure = message.text.replace(' ', '')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['date_departure'] = date_departure
    res_kod_iata = looking_route(message, data)
    if not res_kod_iata:
        bot.send_message(message.chat.id,
                         'Введены неправильные пункты '
                         'отправления или прибытия.\n'
                         'Выберите команду <b>/custom</b> снова'
                         ' и повторите ввод.',
                         parse_mode='html')
        return
    else:
        bot.send_message(message.chat.id, 'Всё Ok. полетели!')
        aeroport_origin = res_kod_iata['origin']['iata']
        aeroport_destination = res_kod_iata['destination']['iata']
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['aeroport_origin'] = aeroport_origin
            data['aeroport_destination'] = aeroport_destination
            data['res_kod_iata'] = res_kod_iata
        url_tickets = (f'https://api.travelpayouts.com/aviasales/'
                       f'v3/prices_for_dates?origin={aeroport_origin}'
                       f'&destination={aeroport_destination}'
                       f'&departure_at={data['date_departure']}&unique=false&sorting=price&'
                       f'direct=false&currency=rub&limit=30&token={TOKEN_TRVL}')
        try:
            result = fact_tickets('GET', url_tickets, params=None).json()
            if result:
                handle_flight_results(message, result, data)
            else:
                bot.send_message(message.chat.id,
                                 'Что-то пошло не так, '
                                 'проверьте соединение с Интернетом')
        except AttributeError:
            bot.send_message(message.chat.id,
                             'Введена неправильная дата'
                             ' отправления.\nВыберите команду'
                             ' <b>/custom</b> снова и повторите'
                             ' ввод.',
                             parse_mode='html')


def handle_flight_results(message: Message, result, data) -> None:
    length = len(result['data'])
    if length == 0:
        bot.send_message(message.chat.id,
                         'По заданным Вами условиям поиска, авиабилетов '
                         'на данное направление не найдено.')
        bot.send_message(message.chat.id,
                         'Выберите команду'
                         ' <b>/custom</b> снова и повторите'
                         ' ввод.',
                         parse_mode='html')
        bot.delete_state(message.from_user.id, message.chat.id)
        return
    elif length == 1:
        bot.send_message(message.chat.id,
                         'По заданным Вами условиям поиска авиабилетов, '
                         'найдено, что приобретался только один билет, на '
                         'данное направление. Цена на него: ' + str(result['data'][0]['price']) + ' руб.')
        data_hist_3 = scr_result(result, message, data['res_kod_iata'], '/custom', message.from_user.id)
        # запрашиваем прогноз погоды на пять дней
        weather_data = weather_forecast(data['destination'])
        scr_weather(message, weather_data, data['destination'])
        try:
            store_func(db, History, *[data_hist_3])
        except IntegrityError:
            bot.send_message(message.chat.id,
                             'Что-то пошло не так, '
                             'при изменении таблицы History')
        bot.send_message(message.chat.id,
                         'Выберите команду'
                         ' <b>/custom</b> снова и повторите'
                         ' ввод.',
                         parse_mode='html')
        bot.delete_state(message.from_user.id, message.chat.id)
        return
    else:
        min_price = result['data'][0]['price']
        max_price = min_price if length == 1 else result['data'][length - 1]['price']
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['min_price'] = min_price
            data['max_price'] = max_price
            data['result'] = result
        bot.send_message(message.chat.id,
                         'Минимальная цена на данное направление: '
                         + str(min_price) + 'руб.')
        bot.send_message(message.chat.id,
                         'Максимальная цена на данное направление: '
                         + str(max_price) + 'руб.')
        bot.send_message(message.chat.id,
                         'Введите минимальную стоимость билета, '
                         'за которую Вы ищите:')
    bot.set_state(message.from_user.id, UserState.AWAITING_MIN_COST, message.chat.id)


@bot.message_handler(state=UserState.AWAITING_MIN_COST)
def handle_min_cost(message: Message) -> None:
    min_cost = message.text.strip()
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['min_cost'] = min_cost
    if data['min_cost'].isdigit() and int(data['min_cost']) > data['min_price']:
        bot.send_message(message.chat.id, 'Введена правильная минимальная цена ' + str(data['min_cost']))
        # Переход к следующему шагу - обработке максимальной стоимости
        handle_max_cost(message)
    else:
        # Введенная стоимость неправильная
        bot.send_message(message.chat.id,
                         f'Минимальная стоимость билета на это направление - '
                         f'{data['min_price']} руб. Введите корректную минимальную'
                         f' стоимость билета, за которую Вы ищите:')
        bot.set_state(message.from_user.id, UserState.AWAITING_MIN_COST, message.chat.id)


def handle_max_cost(message: Message) -> None:
    bot.send_message(message.chat.id,
                     'Введите максимальную стоимость билета, '
                     'за которую Вы ищите:')
    bot.set_state(message.from_user.id, UserState.AWAITING_MAX_COST, message.chat.id)


@bot.message_handler(state=UserState.AWAITING_MAX_COST)
def ask_max_cost(message: Message) -> None:
    max_cost = message.text.strip()
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['max_cost'] = max_cost
    if max_cost.isdigit() and data['min_price'] <= int(max_cost) <= data['max_price']:
        bot.send_message(message.chat.id, 'Введена правильная максимальная цена ' + str(max_cost))
        # Переход к следующему шагу - обработке максимальной стоимости
        handle_trip_direct(message)
    else:
        # Введенная стоимость неправильная
        bot.send_message(message.chat.id,
                         f'Максимальная стоимость билета на это направление - '
                         f'{data['max_price']} руб. Введите корректную максимальную'
                         f' стоимость билета, за которую Вы ищите:')  # Запрашиваем ввод максимальной стоимости снова
        bot.set_state(message.from_user.id, UserState.AWAITING_MAX_COST, message.chat.id)


def handle_trip_direct(message: Message):
    # Создаем инлайн-клавиатуру
    keyboard = types.InlineKeyboardMarkup()
    # Добавляем кнопку "Да"
    yes_button = types.InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(yes_button)
    # Добавляем кнопку "Нет"
    no_button = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(no_button)
    # Отправляем сообщение с клавиатурой
    bot.send_message(message.chat.id,
                     'Выберите искать рейсы с пересадками Да или Нет:',
                      reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    trip_direct = call.data == 'no'
    search_ticket_custom(call.message, trip_direct, call.from_user.id)


def search_ticket_custom(message: Message, direct: str, user_id: int) -> None:
    with bot.retrieve_data(user_id, message.chat.id) as data:
        data['direct'] = direct
    if direct:
        bot.send_message(message.chat.id, 'Прямой рейс.')
    else:
        bot.send_message(message.chat.id, 'Рейс с пересадками.')
    bot.edit_message_reply_markup(message.chat.id, message.message_id)
    url_tickets = (f'https://api.travelpayouts.com/aviasales/'
                   f'v3/prices_for_dates?origin={data['aeroport_origin']}'
                   f'&destination={data['aeroport_destination']}'
                   f'&departure_at={data['date_departure']}&unique=false&sorting=price&'
                   f'direct={str(data["direct"]).lower()}&currency=rub&limit=30&token={TOKEN_TRVL}')
    result = fact_tickets('GET', url_tickets, params=None).json()
    if result:
        new_data = [item for item in result['data'] if int(data['min_cost']) <= item['price'] <= int(data['max_cost'])]
        new_result = new_data[:5] if len(new_data) >= 5 else new_data
        if len(new_result) == 0:
            bot.send_message(message.chat.id,
                             'В заданном Вами диапазоне цен, билетов не найдено.\n'
                             'Выберите команду <b>/custom</b> снова и повторите ввод.', parse_mode='html')
            bot.delete_state(user_id, message.chat.id)
            return
        else:
            result['data'] = new_result
            data_hist_4 = scr_result(result, message, data['res_kod_iata'], '/custom', user_id)
            # запрашиваем прогноз погоды на пять дней
            weather_data = weather_forecast(data['destination'])
            scr_weather(message, weather_data, data['destination'])
            try:
                store_func(db, History, *[data_hist_4])
            except IntegrityError:
                bot.send_message(message.chat.id,
                                 'Что-то пошло не так, '
                                 'при изменении таблицы History')
    else:
        bot.send_message(message.chat.id,
                         'Что-то пошло не так, '
                         'проверьте соединение с Интернетом')
    bot.delete_state(user_id, message.chat.id)


# Обработчик команды /history
@bot.message_handler(commands=['history'], state="*")
def handle_history(message):
    user_id = message.from_user.id
    user = UserTelegram.get_or_none(UserTelegram.user_id == user_id)
    if user is None:
        bot.reply_to(message, "Вы не зарегистрированы. Напишите /start")
        return
    bot.send_message(message.chat.id, 'Вы находитесь на треке поиска истории последних ваших запросов')
    hist: List[History] = user.history.order_by(-History.due_date, -History.hist_id).limit(5)

    result = []
    result.extend(map(str, reversed(hist)))

    if not result:
        bot.send_message(message.from_user.id, "У вас ещё нет задач")
        return
    bot.send_message(message.from_user.id, "\n".join(result))


# выдаёт эхо, если приветствие отвечает
@bot.message_handler(content_types=['text'])
def _all_messages(message):
    text = message.text.lower()
    user = message.from_user.first_name
    if any(word in text for word in hello_lst):
        hello_message = choice(hello_lst)
        bot.send_message(message.chat.id, f'{hello_message} ,'.capitalize() + f'{user}!'.capitalize())
    else:
        bot.send_message(message.chat.id, text.capitalize())


def handle_departure(message: Message, next_state: State) -> None:
    bot.send_message(message.chat.id, "Введите пункт назначения на русском языке:")
    bot.set_state(message.from_user.id, next_state, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['departure'] = message.text


def handle_destination(message: Message, next_state: State) -> None:
    bot.send_message(message.chat.id,
                     'Введите дату вылета из пункта отправления '
                     '(в формате YYYY-MM или YYYY-MM-DD):')
    bot.set_state(message.from_user.id, next_state, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['destination'] = message.text


def looking_route(message: Message, data: Dict) -> Dict[str, Any]:
    bot.send_message(message.chat.id,
                     f'Вы выбрали, пункт отправления:'
                     f' {data['departure']},\nпункт назначения:'
                     f' {data['destination']},\nдата вылета:'
                     f' {data['date_departure']}\nПосмотрим, летают'
                     f' ли туда самолёты?')
    url = (f'https://www.travelpayouts.com/widgets_suggest_params?'
           f'q=Из%20{data['departure']}%20в%20{data['destination']}')
    response = fact_by_IATA("GET", url, params=None)
    return response.json()


# функция вывода найденных билетов по заданным параметрам
def scr_result(response: Dict, message: Message,
               res_kod_iata: Dict, command: str, user: int) -> Dict:
    is_done = True
    for index in response['data']:
        answer = 'Пункт вылета: ' + str(index['origin']) + '\n'
        answer += 'Аэропорт вылета: ' + str(index['origin_airport']) + '\n'
        answer += 'Пункт прилёта: ' + str(index['destination']) + '\n'
        answer += 'Аэропорт прилёта: ' + str(index['destination_airport']) + '\n'
        answer += 'Номер рейса: ' + str(index['flight_number']) + '\n'
        answer += 'Авиакомпания: ' + str(index['airline']) + '\n'
        answer += 'Цена билетов: ' + str(index['price']) + '\n'
        answer += ('Дата и время отправления по MSK: '
                   + str(index['departure_at'])[:10] +
                   ' ' + str(index['departure_at'])[11:16] + '\n')
        hours = index['duration_to'] // 60
        minutes = index['duration_to'] % 60
        if minutes < 10:
            str_min = '0' + str(minutes)
        else:
            str_min = str(minutes)
        answer += 'Время в пути: ' + str(hours) + ':' + str_min + '\n'
        bot.send_message(message.chat.id, answer)
        data_hist['user_id'] = user
        data_hist['command'] = command
        data_hist['request'] = res_kod_iata
        data_hist['due_date'] = datetime.today().strftime(DATE_FORMAT)
        data_hist['is_done'] = is_done
    return data_hist


# вывод на экран бота прогноза на пять дней
def scr_weather(message, response, city):
    bot.send_message(message.chat.id, 'Прогноз погоды на пять дней в городе: ' + city)
    bot.send_message(message.chat.id, '|     Дата      | Погода днём')
    for index in response['list']:
        string = ('|' + datetime.fromtimestamp(index['dt'], tz=timezone.utc).strftime(DATE_FORMAT) +
                  '|' + '{0:+3.0f}'.format(index['temp']['day']) + ' '
                  + index['weather'][0]['description'])
        bot.send_message(message.chat.id, string)


if __name__ == '__main__':
    bot.polling()
