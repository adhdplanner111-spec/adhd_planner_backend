from pydantic import BaseModel, Field


class UpdatePendingOtpSchema(BaseModel):

    otp: str = Field(
        min_length=6,
        max_length=6
    )

    expire_minutes: int = Field(
        ge=1,
        le=30,
        default=5
    )