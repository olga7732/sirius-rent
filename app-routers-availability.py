from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List, Optional
from app.database import get_db
from app.models import User
from app.schemas import RoomResponse
from app.dependencies import get_current_active_user
from app.utils.validators import find_available_rooms
from app.crud import get_room_by_id 

router = APIRouter(prefix="/rooms", tags=["Availability"])

@router.get("/available", response_model=List[RoomResponse])
async def get_available_rooms(
    start: datetime = Query(..., description="Start time (ISO format)"),
    end: datetime = Query(..., description="End time (ISO format)"),
    capacity: Optional[int] = Query(None, ge=1, description="Minimum capacity"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    if start >= end:
        raise HTTPException(status_code=400, detail="Start time must be before end time")
    
    room_ids = await find_available_rooms(start, end, capacity, db)
    rooms = []
    for room_id in room_ids:
        room = await get_room_by_id(room_id, db)
        if room:
            rooms.append(room)
    return rooms