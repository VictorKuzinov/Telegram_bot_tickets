# owm_api
from site_api.core import SiteApiInterface
from setting import TOKEN_OWM

params_OWM = {
    'units': 'metric',
    'lang': 'ru',
    'APPID': TOKEN_OWM
}

geo_position = SiteApiInterface.geo_pos()
fact_by_weather = SiteApiInterface.get_weather()


def _weather_forecast(city: str) -> None:
    latitude, longitude = geo_position(city)
    url = (f'https://pro.openweathermap.org/data/2.5/'
           f'forecast/daily?lat={latitude}&lon={longitude}&cnt=5')
    response = fact_by_weather("GET", url, params=params_OWM)
    data = response.json()
    return data


class WeatherInterface:
    @classmethod
    def weather_forecast(cls):
        return _weather_forecast
