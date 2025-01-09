# site_api.py
import requests
from typing import Dict, Tuple
from geopy.geocoders import Nominatim

def _geo_pos(city: str) -> Tuple[str, str]:
    geolocator = Nominatim(user_agent="TOKEN_AGENT")
    latitude = str(geolocator.geocode(city).latitude)
    longitude = str(geolocator.geocode(city).longitude)
    return latitude, longitude


def _make_response(method: str, url: str, params: Dict, success=200):
    response = requests.request(
        method,
        url,
        params=params
    )

    status_code = response.status_code

    if status_code == success:
        return response

    return status_code


def _get_date_IATA(method: str, url: str, params: Dict, func=_make_response):

    response = func(method, url, params)

    return response


def _get_tickets_trvl(method: str, url: str, params: Dict, func=_make_response):

    response = func(method, url, params)

    return response


def _get_weather(method: str, url: str, params: Dict, func=_make_response):

    response = func(method, url, params)

    return response


class SiteApiInterface():

    @staticmethod
    def get_date_IATA():
        return _get_date_IATA

    @staticmethod
    def get_tickets_trvl():
        return _get_tickets_trvl

    @staticmethod
    def geo_pos():
        return _geo_pos

    @staticmethod
    def get_weather():
        return _get_weather

if __name__ == "__main__":
    _make_response()
    _get_date_IATA()
    _get_tickets_trvl()
    _geo_pos()
    _get_weather()

    SiteApiInterface()
