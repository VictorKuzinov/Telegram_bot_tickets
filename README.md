# Финальная работа по *Курсу «Основы Python. Часть 2»*
## Разработка Телеграм-бот

### Что нужно сделать
Задача максимально приближена к реальной: нужно разработать
Телеграм-бот для заказчика, который хочет вести бизнес в интернете.
В соответствии с ТЗ, бот должен выполнять различные команды
и иметь отзывчивый и понятный интерфейс. Для разработки проекта
используется любой открытый API. 

#### Пишем Телеграм-бот, который: 
С помощью специальных команд бота может сделать следующее:
1. Запросить минимальные значения (команда **/low**).
- Первый запрос делаем к API Базы IATA от Aviasales
Запрос нужен, чтобы определить коды IATA аэропортов, для второго запроса
```python
res_kod_iata = requests.get(f'https://www.travelpayouts.com/'
                            f'widgets_suggest_params?q=Из%20'
                            f'Екатеринбург%20в%20Москва').json()
```
- Данные полученные в результате запроса в формате JSON:
```python
{'origin': {'iata': 'SVX', 'name': 'Yekaterinburg'}, 
 'destination': {'iata': 'MOW', 'name': 'Moscow'}}
```
- Второй запрос для получения стоимости билетов на данное направление:
```python
result = requests.get(f'https://api.travelpayouts.com/aviasales/'
                      f'v3/prices_for_dates?origin=SVX&destination=MOW'
                      f'&departure_at=2024-04&return_at=2024-04'
                      f'&unique=false&sorting=price&direct=false'
                      f'&currency=rub&limit=5&one_way=true&token={Ваш токен}')
```
- Ответ полученный в формате JSON отсортированный по возрастанию 
цены билетов на данное направление в количестве пяти билетов
```python
{'data': [{'flight_number': '294', 'link': '/search/SVX0904MOW09041?
t=5N17126421001712644200000155SVXSVO17127063001712722200000145SVOSVX_558069d65e857ff7f535543df02cd122_7084
&search_date=30032024&expected_price_uuid=ffdfa490-b190-490f-b72e-a3a0afbc4d00
&expected_price_source=share&expected_price_currency=rub&expected_price=7084',
'origin_airport': 'SVX', 'destination_airport': 'SVO', 'departure_at':
'2024-04-09T05:55:00+05:00', 'airline': '5N', 'destination': 'MOW', 
'return_at': '2024-04-09T23:45:00+03:00', 'origin': 'SVX', 'price': 
7084, 'return_transfers': 0, 'duration': 300, 'duration_to': 155, 
'duration_back': 145, 'transfers': 0}, 
{'flight_number': '294', 'link': '/search/SVX0904MOW10041?t=5N17126421001712644200000155SVXSVO17127927001712808600000145SVOSVX_d2346664464bf369f70aded00954d656_7126
&search_date=30032024&expected_price_uuid=c678ab90-2bf1-44d6-9847-a149c8bf1701
&expected_price_source=share&expected_price_currency=rub
&expected_price=7126', 'origin_airport': 'SVX', 'destination_airport':
'SVO', 'departure_at': '2024-04-09T05:55:00+05:00', 'airline': '5N',
'destination': 'MOW', 'return_at': '2024-04-10T23:45:00+03:00', 
'origin': 'SVX', 'price': 7126, 'return_transfers': 0, 'duration': 300,
'duration_to': 155, 'duration_back': 145, 'transfers': 0}, 
{'flight_number': '294', 'link': '/search/SVX0904MOW11041?t=5N17126421001712644200000155SVXSVO17127969001712812500000140SVOSVX_782619ee9a2303efe724ee7ef24ec3b9_7140&search_date=30032024&expected_price_uuid=ae607989-4108-4e22-9162-e1c0a3635201
&expected_price_source=share&expected_price_currency=rub
&expected_price=7140', 'origin_airport': 'SVX', 'destination_airport':
'SVO', 'departure_at': '2024-04-09T05:55:00+05:00', 'airline': '5N',
'destination': 'MOW', 'return_at': '2024-04-11T00:55:00+03:00',
'origin': 'SVX', 'price': 7140, 'return_transfers': 0, 'duration': 295,
'duration_to': 155, 'duration_back': 140, 'transfers': 0},
{'flight_number': '294', 'link': '/search/SVX0904MOW16041?t=5N17126421001712644200000155SVXSVO17132286001713244200000140SVOSVX_e67df0f475b2fea9d40816d36dead467_7140&search_date=30032024&expected_price_uuid=bf7c8b43-b864-45e0-b5b5-35d4d4b6e602&expected_price_source=share
&expected_price_currency=rub&expected_price=7140', 'origin_airport':
'SVX', 'destination_airport': 'SVO', 'departure_at':
'2024-04-09T05:55:00+05:00', 'airline': '5N', 'destination': 
'MOW', 'return_at': '2024-04-16T00:50:00+03:00', 'origin':
'SVX', 'price': 7140, 'return_transfers': 0, 'duration': 295,
'duration_to': 155, 'duration_back': 140, 'transfers': 0}, 
{'flight_number': '294', 'link': '/search/SVX0904MOW24041?t=5N17126421001712644200000155SVXSVO17139240001713939600000140SVOSVX_1dba5067861c88b33f5ea929afca2d1a_7140
&search_date=30032024&expected_price_uuid=160f5144-638d-457e-86ff-579dc615c203
&expected_price_source=share&expected_price_currency=rub&
expected_price=7140', 'origin_airport': 'SVX', 'destination_airport':
'SVO', 'departure_at': '2024-04-09T05:55:00+05:00', 'airline': '5N',
'destination': 'MOW', 'return_at': '2024-04-24T02:00:00+03:00',
'origin': 'SVX', 'price': 7140, 'return_transfers': 0, 'duration': 295,
'duration_to': 155, 'duration_back': 140, 'transfers': 0}],
'currency': 'rub', 'success': True}

```
2. Запросить максимальные значения (команда **/high**).
```python
result = requests.get(f'https://api.travelpayouts.com/aviasales/'
                      f'v3/prices_for_dates?origin=SVX&destination=MOW'
                      f'&departure_at=2024-04&return_at=2024-04'
                      f'&unique=false&sorting=price&direct=false'
                      f'&currency=rub&limit=30&one_way=true&token={Ваш токен}')
```
- Из ответа на данный запрос возьмём 5 последних билета
3. Запросить диапазон значений (команда **/custom**).
```python
result = requests.get(f'https://api.travelpayouts.com/aviasales/'
                      f'v3/prices_for_dates?origin=SVX&destination=MOW'
                      f'&departure_at=2024-04&return_at=2024-04'
                      f'&unique=false&sorting=price&direct=false'
                      f'&currency=rub&limit=30&one_way=true&token={Ваш токен}')
```
- Из ответа на данный запрос возьмём билеты соответствующие критерию
диапазона заданного значений
4. Узнать историю запросов (команда **/history**).
5. Подсказка по командам (команда **/help**)

#### Исходные данные
Данные полученные с помощью API c cайтов: 
- [Travelpayouts](https://support.travelpayouts.com/hc/ru/articles/203956163-Aviasales-API-%D0%B4%D0%BE%D1%81%D1%82%D1%83%D0%BF%D0%B0-%D0%BA-%D0%B4%D0%B0%D0%BD%D0%BD%D1%8B%D0%BC-%D0%B4%D0%BB%D1%8F-%D1%83%D1%87%D0%B0%D1%81%D1%82%D0%BD%D0%B8%D0%BA%D0%BE%D0%B2-%D0%BF%D0%B0%D1%80%D1%82%D0%BD%D1%91%D1%80%D1%81%D0%BA%D0%BE%D0%B9-%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D1%8B)
- [OpenWeather](https://openweathermap.org/api)

#### Методы реализации проекта:
##### Стек:
Python 3.12
PostgreSQL 16.2

#### Архитектура **Монолит**
Состоит из трех модулей:
1) База данных
2) Сайт API
3) Telegram API

##### Слой База данных
Реализован на базе данных SQL Postgre взаимодейтсвие 
с Python осуществляется с помощью библиотеки *peewee*,
реализующая технлогию ORM (объектно-реляционное отображение, 
или преобразование)
Запросы API осуществляется к двум сайтам:
1. Travelpayouts — это платформа, в которую входят партнёрские
программы туристических брендов. На данной платформе мы будем
осуществлять поиск билетов и определять их стоимость.
2. OpenWeather - это платформа рогнозы погоды, текущие прогнозы
и история в быстром и элегантном виде. На данном рессурсе мы 
будем определять прогноз погоды на пять денй вперед от текущей
В проекте задействованы две таблицы в схеме telegram:
- Таблица *usertelegram*:
  - Структура:
```SQL
CREATE TABLE IF NOT EXISTS telegram.usertelegram
(
    user_id bigint NOT NULL DEFAULT nextval('telegram.usertelegram_user_id_seq'::regclass),
    username character varying(255) COLLATE pg_catalog."default" NOT NULL,
    first_name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    last_name character varying(255) COLLATE pg_catalog."default",
    CONSTRAINT usertelegram_pkey PRIMARY KEY (user_id)
)
```
- Таблица *history*:
  - Структура:
```SQL
CREATE TABLE IF NOT EXISTS telegram.history
(
    hist_id integer NOT NULL DEFAULT nextval('telegram.history_hist_id_seq'::regclass),
    user_id integer NOT NULL,
    request character varying(255) COLLATE pg_catalog."default" NOT NULL,
    due_date date NOT NULL,
    is_done boolean NOT NULL,
    CONSTRAINT history_pkey PRIMARY KEY (hist_id),
    CONSTRAINT history_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES telegram.usertelegram (user_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
```

##### Слой Сайт API 
Реализован с помощью библиотеки *request*

##### Слой Telegram API
Реализован с помощью библиотеки *pyTelegramBotAPI*

