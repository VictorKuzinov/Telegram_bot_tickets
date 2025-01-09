# setting.py Для проекта поиска билетов

# Токены укажите ваши ключи и токены
TOKEN_TLG = 'your token telegram bot'
TOKEN_OWM = 'your API-key for site OWM'
TOKEN_AGENT = "your API-key for site OpenWeather"
TOKEN_TRVL = 'your API-key for site Travelpayouts'


# данные для доступа к базе данных
DB_HOST = 'localhost'
DB_PORT = 5432
DB_USER = 'postgres'
DB_PASSWORD = 'your password'  # укажите свой пароль к базе Postgres
DB_DATABASE = 'postgres'
# укажите свой пароль к базе Postgres
DATABASE_URL = 'postgresql://postgres:your_password@localhost/postgres'
SCHEMA_NAME = 'telegram'


# поддерживаемые команды
DEFAULT_COMMANDS = (
    ('low', 'Запросить 5 дешевых билетов'),
    ('high', "Запросить 5 дорогих билетов"),
    ('custom', 'Запросить 5 билетов в диапазоне цен'),
    ('history', 'Показать историю 5 запросов'),
    ('help', 'Показать подсказку бота'),
)

# формат назначенной даты у задачи
DATE_FORMAT = "%d.%m.%Y"

# список приветствий
hello_lst = ['привет', 'добрый день', 'здравствуй', 'hello', 'здорово']
