class TripRouteExecutorNode:

    def __init__(
            self,
            route_service
    ):
        self.route_service = route_service

    async def __call__(
            self,
            state
    ):
        selection = state.get('plan_selection')

        if selection is None:
            return {
                "status": "failed",
                "error": "缺少 PlanSelection",
            }

        routes = []

        attractions = {
            item.id: item
            for item in state.get(
                'attractions',
                []
            )
        }

        for day in selection.days:

            selected = []

            for attraction_id in day.attraction_ids:

                attraction = attractions.get(
                    attraction_id
                )

                if attraction:
                    selected.append(attraction)

            for i in range(len(selected) - 1):
                origin = selected[i]
                destination = selected[i + 1]

                try:
                    route = await self.route_service.transit(
                        origin_address=origin.address,
                        destination_address=destination.address,
                        city=state['request'].city,
                    )

                    routes.append(
                        {
                            "date": day.date,
                            "origin": origin.id,
                            "destination": destination.id,
                            "route": route,
                        }
                    )

                except Exception as e:

                    routes.append(
                        {
                            "date": day.date,
                            "origin": origin.id,
                            "destination": destination.id,
                            "error": str(e),
                        }
                    )

        return {
            "routes": routes,
            "status": "routes_completed",
            "error": None,
        }