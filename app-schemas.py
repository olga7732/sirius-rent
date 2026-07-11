from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from app.models import UserRole, BookingStatus

# === User ===
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: int
    username: str
    role: UserRole
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# === Room ===
class RoomCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    capacity: int = Field(..., ge=1)
    equipment: List[str] = []

class RoomUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    capacity: Optional[int] = Field(None, ge=1)
    equipment: Optional[List[str]] = None

class RoomResponse(BaseModel):
    id: int
    name: str
    capacity: int
    equipment: List[str]
    
    class Config:
        from_attributes = True

# === Booking ===
class BookingCreate(BaseModel):
    room_id: int
    start_time: datetime
    end_time: datetime
    
    @validator('end_time')
    def validate_time_range(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

class BookingResponse(BaseModel):
    id: int
    room_id: int
    user_id: int
    start_time: datetime
    end_time: datetime
    status: BookingStatus
    
    class Config:
        from_attributes = True

# === Filters ===
class RoomFilter(BaseModel):
    capacity_min: Optional[int] = None
    equipment: Optional[str] = None