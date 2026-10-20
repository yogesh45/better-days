from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
class UserLogin(BaseModel):
    email: EmailStr
    password: str
class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    bio: str
    model_config = ConfigDict(from_attributes=True)
class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
class RecipeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str = ""
    category: str = "Other"
    cooking_minutes: int = Field(default=20, ge=1, le=1440)
    servings: int = Field(default=2, ge=1, le=100)
    image_url: str | None = None
    ingredients: list[str] = Field(min_length=1, max_length=100)
    steps: list[str] = Field(min_length=1, max_length=100)
    is_public: bool = True
class RecipeOut(BaseModel):
    id: int; user_id: int; title: str; description: str; category: str
    cooking_minutes: int; servings: int; image_url: str | None
    ingredients: list[str]; steps: list[str]; is_public: bool; created_at: datetime
    model_config = ConfigDict(from_attributes=True)
class HabitIn(BaseModel):
    habit_key: str = Field(min_length=1, max_length=40)
    completed: bool = True
    checkin_date: date | None = None
class WaterIn(BaseModel):
    glasses: int = Field(ge=0, le=30)
    log_date: date | None = None
class PostIn(BaseModel):
    body: str = Field(min_length=1, max_length=1000)
class PostOut(BaseModel):
    id: int; user_id: int; name: str; body: str; created_at: datetime; cheers: int; cheered_by_me: bool
class ChallengeOut(BaseModel):
    id: int; title: str; description: str; duration_days: int; members: int; joined: bool
class ProfileUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    bio: str = Field(default="", max_length=240)
