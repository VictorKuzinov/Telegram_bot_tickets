from typing import Dict, List, TypeVar

from peewee import ModelSelect

from database.models import BaseModel, db


T = TypeVar("T")


def _store_date(database: db, model: T, *data: List[Dict]) -> None:
    with database.atomic():
        model.insert_many(*data).execute()


def _retrieve_all_data(database: db, model: T, *columns: BaseModel) -> ModelSelect:
    with database.atomic():
        response = model.select(*columns)
    return response


class CRUDInteface():

    @staticmethod
    def create():
        return _store_date

    @staticmethod
    def retrieve():
        return _retrieve_all_data
