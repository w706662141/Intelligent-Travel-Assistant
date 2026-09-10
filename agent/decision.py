from enum import Enum


class DecisionType(str, Enum):

    TOOL_CALL = 'tool_call'

    FINAL_ANSWER = 'final_answer'

    ABORT = 'abort'
