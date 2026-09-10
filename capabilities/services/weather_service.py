from infrastructure.amap.gateways.weather import AmapWeatherGateway

from infrastructure.amap.mappers.weather import AmapWeatherMapper


class WeatherService:

    def __init__(self,
                 weather_gateway: AmapWeatherGateway):
        self.weather_gateway = weather_gateway

    async def query_weather(
            self,
            city):
        raw_data = await self.weather_gateway.query(city)

        return AmapWeatherMapper.to_domain(raw_data)
