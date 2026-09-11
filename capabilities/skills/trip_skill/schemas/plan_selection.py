from pydantic import BaseModel, Field


class DaySelection(BaseModel):
    date: str

    attraction_ids: list[str] = Field(
        default_factory=list
    )

    hotel_id: str | None = None

    meal_ids: list[str] = Field(
        default_factory=list
    )

    description: str = ''


class PlanSelection(BaseModel):
    days: list[DaySelection] = Field(
        default_factory=list
    )

    overall_suggestion: str = ''
