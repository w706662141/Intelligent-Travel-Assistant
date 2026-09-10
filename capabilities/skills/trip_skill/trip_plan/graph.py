# from langgraph.graph import StateGraph, START, END
#
# from capabilities.skills.trip_skill.nodes.planning_node import TripPlanningNode
# from capabilities.skills.trip_skill.nodes.validation_node import TripPlanValidationNode
# from capabilities.skills.trip_skill.trip_plan.router import route_after_validation
# from capabilities.skills.trip_skill.trip_plan.state import TripPlanState
#
#
# class TripPlanGraph:
#
#     def __init__(
#             self,
#             planning_service
#     ):
#         self.planning_node = (
#             TripPlanningNode(
#                 planning_service
#             )
#         )
#
#         self.validation_node = (
#             TripPlanValidationNode()
#         )
#
#     def build(self):
#         graph = StateGraph(
#             TripPlanState
#         )
#         # =========================
#         # Nodes
#         # =========================
#
#         graph.add_node(
#             'planning',
#             self.planning_node
#         )
#         graph.add_node(
#             'validation',
#             self.validation_node
#         )
#
#         # =========================
#         # START
#         # =========================
#
#         graph.add_edge(
#             START,
#             'planning'
#         )
#
#         # =========================
#         # Planning -> Validation
#         # =========================
#
#         graph.add_edge(
#             'planning',
#             'validation',
#         )
#
#         # =========================
#         # Validation -> ...
#         # =========================
#
#         graph.add_conditional_edges(
#             'validation',
#             route_after_validation,
#             {
#                 "planning": "planning",
#                 END: END,
#             },
#         )
#
#         return graph.compile()
from langgraph.graph import StateGraph
from langgraph.graph import (
    StateGraph,
    START,
    END,
)
from capabilities.skills.trip_skill.nodes.data_collection_node import TripDataCollectionNode
from capabilities.skills.trip_skill.nodes.planning_node import TripPlanningNode
from capabilities.skills.trip_skill.nodes.validation_node import TripPlanValidationNode
from capabilities.skills.trip_skill.trip_plan.router import route_after_validation
from capabilities.skills.trip_skill.trip_plan.state import TripPlanState


class TripPlanGraph:

    def __init__(
            self,
            planning_service,
            llm,
    ):
        self.data_collection_node = (
            TripDataCollectionNode(
                planning_service
            )
        )

        self.planning_node = (
            TripPlanningNode(
                llm
            )
        )

        self.validation_node = (
            TripPlanValidationNode()
        )

    def build(self):
        graph = StateGraph(
            TripPlanState
        )

        # =========================
        # Nodes
        # =========================

        graph.add_node(
            'collect_data',
            self.data_collection_node,
        )

        graph.add_node(
            'planning',
            self.planning_node
        )

        graph.add_node(
            'validation',
            self.validation_node
        )

        # =========================
        # START
        # =========================

        graph.add_edge(
            START,
            'collect_data',
        )

        # =========================
        # Data -> Planning
        # =========================

        graph.add_edge(
            'collect_data',
            'planning'
        )

        graph.add_edge(
            'planning',
            'validation'
        )

        # =========================
        # Validation -> ...
        # =========================

        graph.add_conditional_edges(
            'validation',
            route_after_validation,
            {
                'planning': 'planning',
                END: END
            },
        )

        return graph.compile()
