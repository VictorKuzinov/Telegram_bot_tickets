# models.py

import json
from peewee import (
    AutoField,
    BooleanField,
    CharField,
    DateField,
    ForeignKeyField,
    Model,
    PostgresqlDatabase,
    BigAutoField,
)

from setting import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_DATABASE, SCHEMA_NAME, DATE_FORMAT

db = PostgresqlDatabase(
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_DATABASE
)


# Создание схемы
def create_schema() -> None:
    db.execute_sql(f'CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}')


class BaseModel(Model):
    class Meta:
        database = db
        schema = SCHEMA_NAME


# создаём таблицу users в базе данных
class UserTelegram(BaseModel):
    user_id = BigAutoField(primary_key=True)  # первичный ключ модели,
    # будет совпадать с Telegram ID. Это значит, что он будет
    # уникальным для всей таблицы.
    username = CharField()  # никнейм в Telegram
    first_name = CharField()  # имя в Telegram
    last_name = CharField(null=True)  # фамилия в Telegram.
    # Может быть не указана, поэтому ставим null=True.


class History(BaseModel):
    hist_id = AutoField()  # hist_id — ID история. AutoField показывает,
    # что это первичный ключ, а значение будет автоматически
    # увеличиваться на единицу. Аналог PRIMARY KEY AUTOINCREMENT.
    user = ForeignKeyField(UserTelegram, backref="history")  # user
    # — внешний ключ, ссылающийся на пользователя;
    # backref создаёт обратную ссылку: мы сможем получить задачи
    # пользователя с помощью user.
    command = CharField(null=True)  # команда выполняемая ботом
    request = CharField()  # title — название задачи
    due_date = DateField()  # дата выполнения запроса
    is_done = BooleanField(default=False)  # выполнен Ваш запрос удачно?

    def __str__(self) -> str:
        request_json = str(self.request).replace("'", '"')
        data = json.loads(request_json)
        str_request = ('От куда вылетаем: ' + data['origin']['name'] +
                       ', куда летим: ' + data['destination']['name'])
        return '{hist_id}. Команда {command} - {request} - Дата запроса - {due_date}. '.format(
            hist_id=self.hist_id,
            command=self.command,
            request=str_request,
            due_date=self.due_date.strftime(DATE_FORMAT)
        )

# Вызов функции для создания схемы при инициализации

def create_models() -> None:
    create_schema()
    db.create_tables(BaseModel.__subclasses__())


create_models()
