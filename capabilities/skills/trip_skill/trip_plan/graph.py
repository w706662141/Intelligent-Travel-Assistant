from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from capabilities.skills.trip_skill.nodes.builder_node import (
    TripPlanBuilderNode,
)

from capabilities.skills.trip_skill.nodes.decision_node import (
    TripResourceDecisionNode,
)

from capabilities.skills.trip_skill.nodes.meal_executor_node import (
    TripMealExecutorNode,
)

from capabilities.skills.trip_skill.nodes.planning_node import (
    TripPlanningNode,
)

from capabilities.skills.trip_skill.nodes.resource_executor_node import (
    TripResourceExecutorNode,
)

from capabilities.skills.trip_skill.nodes.route_executor_node import (
    TripRouteExecutorNode,
)

from capabilities.skills.trip_skill.nodes.validation_node import (
    TripPlanValidationNode,
)

from capabilities.skills.trip_skill.trip_plan.router import (
    route_after_validation,
)

from capabilities.skills.trip_skill.trip_plan.state import (
    TripPlanState,
)


class TripPlanGraph:

    def __init__(
            self,
            attraction_service,
            hotel_service,
            # meal_service,
            weather_service,
            # route_service,
            llm,
    ):

        self.decision_node = (
            TripResourceDecisionNode(llm)
        )

        self.resource_executor = (
            TripResourceExecutorNode(
                attraction_service=attraction_service,
                hotel_service=hotel_service,
                weather_service=weather_service,
            )
        )

        self.planning_node = (
            TripPlanningNode(llm)
        )

        # self.meal_executor = (
        #     TripMealExecutorNode(
        #         meal_service=meal_service,
        #     )
        # )
        #
        # self.route_executor = (
        #     TripRouteExecutorNode(
        #         route_service=route_service,
        #     )
        # )

        self.builder_node = (
            TripPlanBuilderNode()
        )

        self.validation_node = (
            TripPlanValidationNode()
        )

    def build(self):

        graph = StateGraph(
            TripPlanState
        )

        # ======================================
        # Nodes
        # ======================================

        graph.add_node(
            "decision",
            self.decision_node,
        )

        graph.add_node(
            "collect_resources",
            self.resource_executor,
        )

        graph.add_node(
            "planning",
            self.planning_node,
        )

        # graph.add_node(
        #     "meal",
        #     self.meal_executor,
        # )
        #
        # graph.add_node(
        #     "route",
        #     self.route_executor,
        # )

        graph.add_node(
            "build",
            self.builder_node,
        )

        graph.add_node(
            "validation",
            self.validation_node,
        )

        # ======================================
        # Main Flow
        # ======================================

        graph.add_edge(
            START,
            "decision",
        )

        graph.add_edge(
            "decision",
            "collect_resources",
        )

        graph.add_edge(
            "collect_resources",
            "planning",
        )

        # graph.add_edge(
        #     "planning",
        #     "meal",
        # )
        #
        # graph.add_edge(
        #     "meal",
        #     "route",
        # )
        #
        # graph.add_edge(
        #     "route",
        #     "build",
        # )

        graph.add_edge(
            "planning",
            "validation",
        )

        # ======================================
        # Validation
        # ======================================

        graph.add_conditional_edges(
            "validation",
            route_after_validation,
            {
                "planning": "planning",
                END: END,
            },
        )

        return graph.compile()