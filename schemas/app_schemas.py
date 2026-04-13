from pydantic import BaseModel, Field

class BotCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    allowed_domain: str = Field(..., description="Example: mysite.com")

class BotOut(BaseModel):
    id: int
    name: str
    api_key: str
    allowed_domain: str

    class Config:
        from_attributes = True

class BotShortInfo(BaseModel):
    id: int
    name: str
    api_key: str
    allowed_domain: str

    class Config:
        from_attributes = True