import asyncio

from capabilities.skills.trip_skill.trip_plan.state import TripPlanState


class TripResourceExecutorNode:

    SUPPORTED_RESOURCES = {
        "attraction",
        "hotel",
        "weather",
    }

    def __init__(
            self,
            attraction_service,
            hotel_service,
            weather_service,
    ):
        self.attraction_service = attraction_service
        self.hotel_service = hotel_service
        self.weather_service = weather_service

    async def __call__(
            self,
            state: TripPlanState
    ):
        request = state['request']
        decision = state.get('resource_decision')

        if decision is None:
            return {
                'status': 'failed',
                'error': "缺少 ResourceDecision",
            }

        resource_types = {
            item.resource_type
            for item in decision.requests
        }

        tasks = {}

        if 'attraction' in resource_types:
            tasks['attractions'] = (
                self.attraction_service.search_with_details(
                    city=request.city,
                    keyword='景点',
                    limit=10,
                )
            )

        if 'hotel' in resource_types:
            tasks['hotel'] = (
                self.hotel_service.search(
                    city=request.city,
                    limit=5
                )
            )

        if "weather" in resource_types:
            tasks["weather"] = (
                self.weather_service.query_weather(
                    request.city
                )
            )

        results = {}

        if tasks:

            keys = list(tasks.keys())

            values = await asyncio.gather(
                *tasks.values(),
                return_exceptions=True,
            )

            for key, value in zip(keys, values):
                if isinstance(value, Exception):
                    return {
                        "status": "failed",
                        "error": (
                            f"{key}资源获取失败: "
                            f"{type(value).__name__}: {value}"
                        ),
                    }

                results[key] = value

        return {
            **results,
            "status": "resources_collected",
            "error": None,
        }
