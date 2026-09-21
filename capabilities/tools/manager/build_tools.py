from capabilities.subagents.trip_subagent.subagent import (
    TripSubAgent,
)

from capabilities.tools import (
    create_weather_tool,
    create_route_tools,
    create_meal_tools,
    create_hotel_tools,
    create_attraction_tools,
)

from capabilities.services import (
    HotelService,
    WeatherService,
    RouteService,
    MealService,
    AttractionService,
    GeocodeService,
)

from capabilities.tools.manager.tool_registry import (
    ToolRegistry,
)

from capabilities.tools.trip_subagent_tool import (
    create_trip_subagent_tool,
)

from config.settings import settings

from infrastructure.amap.gateways.poi import (
    AmapPOIGateway,
)

from infrastructure.amap.gateways.route import (
    AmapRouteGateway,
)

from infrastructure.amap.gateways.weather import (
    AmapWeatherGateway,
)

from infrastructure.amap.gateways.geocode import (
    AmapGeocodeGateway,
)

from infrastructure.mcp.clients.amap_client import (
    AmapMCPClient,
)


async def build_tools_registry():
    # ==========================================
    # MCP Client
    # ==========================================

    client = AmapMCPClient(
        api_key=settings.AMAP_MAPS_API_KEY
    )

    await client.connect()

    # ==========================================
    # Gateways
    # ==========================================

    poi_gateway = AmapPOIGateway(
        client
    )

    weather_gateway = AmapWeatherGateway(
        client
    )

    route_gateway = AmapRouteGateway(
        client
    )

    amap_geocode_gateway = AmapGeocodeGateway(
        client
    )

    # ==========================================
    # Services
    # ==========================================

    geocode_service = GeocodeService(
        amap_geocode_gateway
    )

    attraction_service = AttractionService(
        poi_gateway
    )

    hotel_service = HotelService(
        poi_gateway,
        geocode_service
    )

    weather_service = WeatherService(
        weather_gateway
    )

    meal_service = MealService(
        poi_gateway,
        geocode_service
    )

    route_service = RouteService(
        route_gateway
    )

    # ==========================================
    # Resource Tools
    #
    # TripSubAgent 只能使用这些 Tool
    # ==========================================

    attraction_tools = (
        create_attraction_tools(
            attraction_service
        )
    )

    hotel_tools = (
        create_hotel_tools(
            hotel_service
        )
    )

    weather_tools = (
        create_weather_tool(
            weather_service
        )
    )

    meal_tools = (
        create_meal_tools(
            meal_service
        )
    )

    resource_tools = (
            attraction_tools
            + hotel_tools
            + weather_tools
            + meal_tools
    )

    # ==========================================
    # Route Tools
    #
    # 只属于 MainAgent
    # ==========================================

    route_tools = (
        create_route_tools(
            route_service
        )
    )

    # ==========================================
    # MainAgent Tools
    # ==========================================

    main_tools = (
            resource_tools
            + route_tools
    )

    # ==========================================
    # TripSubAgent
    #
    # 注意：
    # 这里只传 resource_tools
    #
    # 不传 route_tools
    # ==========================================

    trip_subagent = TripSubAgent(
        tools=resource_tools,
        max_iterations=15,
    )

    delegate_trip_tool = (
        create_trip_subagent_tool(
            trip_subagent
        )
    )

    # ==========================================
    # Registry
    # ==========================================

    registry = ToolRegistry()

    registry.register(
        main_tools
    )

    registry.register(
        [
            delegate_trip_tool
        ]
    )

    return registry
