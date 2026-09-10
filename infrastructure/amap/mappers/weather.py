from schemas.weather_info import WeatherInfo


class AmapWeatherMapper:

    @staticmethod
    def parse_int(value):
        if value is None:
            return 0

        try:
            return int(
                str(value)
                    .replace("°C", "")
                    .replace("℃", "")
                    .replace("°", "")
                    .strip()
            )
        except ValueError:
            return 0

    @classmethod
    def to_domain(cls,
                  data: dict,
                  ) -> list[WeatherInfo]:

        result = []

        forecasts = data.get(
            'forecasts',
            []
        )

        for cast in forecasts:
            result.append(
                WeatherInfo(
                    date=cast.get(
                        'date',
                        "",
                    ),
                    day_weather=cast.get(
                        'dayweather',
                        '',
                    ),
                    night_weather=cast.get(
                        'nightweather',
                        "",
                    ),
                    day_temp=cls.parse_int(
                        cast.get(
                            "daytemp",
                            0,
                        )
                    ),
                    night_temp=cls.parse_int(
                        cast.get(
                            "nighttemp",
                            0,
                        )
                    ),
                    wind_direction=cast.get(
                        "daywind",
                        "",
                    ),
                    wind_power=cast.get(
                        "daypower",
                        "",
                    ),
                )
            )

        return result
