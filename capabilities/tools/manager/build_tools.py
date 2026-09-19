from capabilities.skills.trip_skill.trip_plan.skill import TripPlanSkill
from capabilities.subagents.trip_subagent.subagent import TripSubAgent
from capabilities.tools import (create_weather_tool,
                                create_route_tools,
                                create_meal_tools,
                                create_hotel_tools,
                                create_attraction_tools,
                                create_trip_plan_tool
                                )

from capabilities.services import (
    HotelService,
    WeatherService,
    RouteService,
    MealService,
    AttractionService,
    GeocodeService,

)

from capabilities.tools.manager.tool_registry import ToolRegistry
from config.settings import settings
from infrastructure.amap.gateways.poi import AmapPOIGateway
from infrastructure.amap.gateways.route import AmapRouteGateway
from infrastructure.amap.gateways.weather import AmapWeatherGateway
from infrastructure.amap.gateways.geocode import AmapGeocodeGateway
from infrastructure.core.llm import get_agnes_model
from infrastructure.mcp.clients.amap_client import AmapMCPClient
from capabilities.tools.trip_subagent_tool import (
    create_trip_subagent_tool,
)

async def build_tools_registry():
    client = AmapMCPClient(api_key=settings.AMAP_MAPS_API_KEY)

    await client.connect()

    poi_gateway = AmapPOIGateway(client)
    weather_gateway = AmapWeatherGateway(client)
    route_gateway = AmapRouteGateway(client)
    amap_geocode_gateway = AmapGeocodeGateway(client)

    gecode_service = GeocodeService(amap_geocode_gateway)
    attraction_service = AttractionService(poi_gateway)
    hotel_service = HotelService(poi_gateway, gecode_service)
    weather_service = WeatherService(weather_gateway)
    meal_service = MealService(poi_gateway, gecode_service)
    route_service = RouteService(route_gateway)

    tools = []

    registry = ToolRegistry()

    tools.extend(
        create_attraction_tools(
            attraction_service
        )
    )

    tools.extend(
        create_hotel_tools(
            hotel_service
        )
    )

    tools.extend(
        create_weather_tool(
            weather_service
        )
    )

    # model = get_agnes_model()
    # trip_plan_model_with_tools = model.bind_tools(tools)

    tools.extend(
        create_meal_tools(
            meal_service
        )
    )

    tools.extend(
        create_route_tools(
            route_service
        )
    )
    #
    # trip_plan_skill = TripPlanSkill(
    #     attraction_service=attraction_service,
    #     hotel_service=hotel_service,
    #     # meal_service=meal_service,
    #     weather_service=weather_service,
    #     # route_service=route_service,
    #     llm=trip_plan_model_with_tools,
    # )

    # tools.extend(
    #     create_trip_plan_tool(
    #         trip_plan_skill
    #     )
    # )

    travel_tools = tools

    trip_subagent = TripSubAgent(
        tools=travel_tools,
        max_iterations=15,
    )

    delegate_trip_tool = (
        create_trip_subagent_tool(
            trip_subagent
        )
    )
    registry.register(tools)
    # 新 SubAgent 委托 Tool
    registry.register(
        [delegate_trip_tool]
    )
    return registry
