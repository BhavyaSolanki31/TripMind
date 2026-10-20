
from datetime import date
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TripRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    origin: str = Field(min_length=1, max_length=100)
    destination: str = Field(min_length=1, max_length=100)
    start_date: date
    end_date: date
    travelers: int = Field(ge=1, le=50)
    total_budget: int = Field(gt=0)
    interests: list[str] = Field(min_length=1)

    @field_validator("origin", "destination")
    @classmethod
    def validate_location(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Location cannot be blank.")
        return value

    @field_validator("interests")
    @classmethod
    def validate_interests(cls, value: list[str]) -> list[str]:
        cleaned = [interest.strip() for interest in value]

        if any(not interest for interest in cleaned):
            raise ValueError("Interests cannot contain blank values.")

        return cleaned

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError("End date must be after start date.")
        return self
