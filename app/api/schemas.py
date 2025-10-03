from pydantic import BaseModel, AnyUrl, field_validator, EmailStr
from typing import Optional, Literal

Channel = Literal["email", "webpush", "telegram", "discord"]

class TrackRequest(BaseModel):
    url: AnyUrl
    target_price: Optional[float] = None
    drop_percent: Optional[float] = None
    channel: Channel
    endpoint: str  # email ou endpoint VAPID

    @field_validator("target_price", "drop_percent")
    @classmethod
    def non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("deve ser >= 0")
        return v

class ProductOut(BaseModel):
    id: int
    url: str
    domain: str
    title: Optional[str]
    currency: str
    current_price: Optional[float]
    in_stock: Optional[bool]

    class Config:
        from_attributes = True

class PricePoint(BaseModel):
    price: float
    captured_at: str
