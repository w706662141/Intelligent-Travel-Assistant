from langgraph.graph import END

from capabilities.skills.trip_skill.trip_plan.state import TripPlanState


def route_after_validation(
        state: TripPlanState,
):
    errors = state.get(
        "validation_errors",
        [],
    )

    if not errors:
        return END

    replan_count = state.get(
        "replan_count",
        0
    )

    max_replan_count = state.get(
        "max_replan_count",
        1
    )

    if replan_count < max_replan_count:
        return "planning"

    return END
