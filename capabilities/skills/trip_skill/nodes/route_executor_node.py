from typing import Any

from capabilities.skills.trip_skill.trip_plan.state import TripPlanState


class TripRouteExecutorNode:

    def __init__(
            self,
            route_service
    ):
        self.route_service = route_service

    async def __call__(
            self,
            state: TripPlanState,
    ):
        selection = state.get('plan_selection')

        if selection is None:
            return {
                "status": "failed",
                "error": "缺少 PlanSelection",
            }

        request = state['request']

        attractions = {
            item.id: item
            for item in state.get(
                'attractions',
                []
            )
            if item.id
        }

        routes: list[dict[str, Any]] = []

        errors: list[str] = []

        for day in selection.days:

            selected = []

            for attraction_id in day.attraction_ids:

                attraction = attractions.get(
                    attraction_id
                )

                if attraction:
                    selected.append(attraction)

            # 一个景点无法形成路线
            if len(selected) < 2:
                continue

            for i in range(len(selected) - 1):
                origin = selected[i]
                destination = selected[i + 1]

                try:
                    route = await self._execute_route(
                        mode=day.transport_mode,
                        origin_address=origin.address,
                        destination_address=destination.address,
                        city=request.city,
                    )

                    routes.append(
                        {
                            "date": day.date,
                            "transport_mode": day.transport_mode,
                            "origin_id": origin.id,
                            "origin_name": origin.name,
                            "destination_id": destination.id,
                            "destination_name": destination.name,
                            "route": route,
                        }
                    )

                except Exception as e:

                    error_message = (
                        f"{day.date} "
                        f"{origin.name} -> "
                        f"{destination.name} "
                        f"路线规划失败: "
                        f"{type(e).__name__}: {e}"
                    )

                    errors.append(
                        error_message
                    )

                    routes.append(
                        {
                            "date": day.date,
                            "transport_mode": day.transport_mode,
                            "origin_id": origin.id,
                            "origin_name": origin.name,
                            "destination_id": destination.id,
                            "destination_name": destination.name,
                            "route": None,
                            "error": str(e),
                        }
                    )

        return {
            "routes": routes,
            "status": "routes_completed",
            "error": None,
        }

    async def _execute_route(
            self,
            mode: str,
            origin_address: str,
            destination_address: str,
            city: str,
    ):
        if mode == 'walking':
            return await self.route_service.walking(
                origin_address=origin_address,
                destination_address=destination_address,
                city=city,
            )

        if mode == "driving":
            return await self.route_service.driving(
                origin_address=origin_address,
                destination_address=destination_address,
                city=city,
            )
        if mode == "bicycling":
            return await self.route_service.bicycling(
                origin_address=origin_address,
                destination_address=destination_address,
                city=city,
            )

        if mode == "transit":
            return await self.route_service.transit(
                origin_address=origin_address,
                destination_address=destination_address,
                city=city,
            )

        raise ValueError(
            f"不支持的交通方式: {mode}"
        )
