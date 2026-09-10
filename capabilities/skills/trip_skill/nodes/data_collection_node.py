from capabilities.services import TripPlanningService
from capabilities.skills.trip_skill.trip_plan.state import TripPlanState


class TripDataCollectionNode:

    def __init__(
            self,
            planning_service: TripPlanningService,
    ):
        self.planning_service = (
            planning_service
        )

    async def __call__(
            self,
            state: TripPlanState,
    ):
        request = state['request']

        try:
            data = (
                await self.planning_service.collect_data(
                    city=request.city,
                    start_date=request.start_date,
                    end_date=request.end_date,
                    preferences=request.preferences
                )
            )
            return {
                "attractions": data["attractions"],
                "hotels": data["hotels"],
                "weather": data["weather"],
                "error": None,
            }
        except Exception as e:
            import traceback

            traceback.print_exc()

            return {
                "status": "failed",
                "error": f"{type(e).__name__}: {e}",
            }
