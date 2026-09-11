from capabilities.skills.trip_skill.prompts.trip_decision_prompt import TRIP_DECISION_PROMPT
from capabilities.skills.trip_skill.schemas.resource_decision import ResourceDecision
from capabilities.skills.trip_skill.trip_plan.state import TripPlanState


class TripResourceDecisionNode:

    def __init__(
            self,
            llm
    ):
        self.structured_llm = (
            llm.with_structured_output(ResourceDecision)
        )

    async def __call__(self, state: TripPlanState):
        request = state['request']

        prompt = TRIP_DECISION_PROMPT.invoke(
            {
                'city': request.city,
                "start_date": request.start_date,
                "end_date": request.end_date,
                "travelers": request.travelers,
                "budget": request.budget,
                "preferences": request.preferences,

            }

        )

        try:
            decision = await self.structured_llm.ainvoke(
                prompt
            )

            return {
                "resource_decision": decision,
                "status": "resource_decided",
                "error": None,
            }

        except Exception as e:

            return {

                "status": "failed",

                "error": f"{type(e).__name__}: {e}",

            }
