from pydantic import BaseModel, Field
from typing import Optional

class BotSettings(BaseModel):
    theme_color: str = Field(default="#4f46e5", description="HEX color for widget")
    system_prompt: str = Field(
        default="You are a helpful customer service assistant.", 
        description="Instruction for AI"
    )

class BotCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    allowed_domain: str = Field(..., description="Example: mysite.com")

    settings: Optional[BotSettings] = Field(default_factory=BotSettings)

class BotOut(BaseModel):
    id: int
    name: str
    api_key: str
    allowed_domain: str
    settings: BotSettings

    class Config:
        from_attributes = True

class BotShortInfo(BaseModel):
    id: int
    name: str
    api_key: str
    allowed_domain: str

    class Config:
        from_attributes = True