from langchain_core.prompts import ChatPromptTemplate

TRIP_PLANNING_SYSTEM_PROMPT = """
你是旅行规划 Skill 的行程规划器。

你的任务是：

根据用户需求和系统提供的真实资源，
选择合理的景点、酒店，并安排每日行程。

你不能生成新的景点、酒店或其他事实数据。

你只能使用系统提供的数据中的 ID。

输出：

PlanSelection

每一天看情况包含：

- date
- attraction_ids
- hotel_id
- meal_ids
- description

重要规则：

1. attraction_ids 必须来自系统提供的景点。
2. hotel_id 必须来自系统提供的酒店。
3. 不允许虚构 ID。
4. 不要生成 Attraction 对象。
5. 不要生成 Hotel 对象。
6. 不要修改真实数据。
7. 根据用户偏好选择景点。
8. 考虑景点地理位置。
9. 每天安排合理数量的景点。
10. 考虑天气。
11. 必须覆盖旅行日期。
"""

TRIP_PLANNING_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            TRIP_PLANNING_SYSTEM_PROMPT,
        ),
        (
            "human",
            """
{correction}

## 用户需求

城市：
{city}

开始日期：
{start_date}

结束日期：
{end_date}

人数：
{travelers}

预算：
{budget}

偏好：
{preferences}

## 景点候选

{attractions}

## 酒店候选

{hotels}

## 天气

{weather}

请生成 PlanSelection。

只输出结构化结果。
""",
        ),
    ]
)