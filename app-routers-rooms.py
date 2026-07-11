from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.database import get_db
from app.models import Room
from app.schemas import RoomCreate, RoomUpdate, RoomResponse, RoomFilter
from app.dependencies import get_current_admin_user, get_current_active_user
from app.models import User

router = APIRouter(prefix="/rooms", tags=["Rooms"])

@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_data: RoomCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    new_room = Room(**room_data.dict())
    db.add(new_room)
    await db.commit()
    await db.refresh(new_room)
    return new_room

@router.get("/", response_model=List[RoomResponse])
async def get_rooms(
    capacity_min: Optional[int] = Query(None, ge=1),
    equipment: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    query = select(Room)
    if capacity_min:
        query = query.where(Room.capacity >= capacity_min)
    if equipment:
        query = query.where(Room.equipment.contains([equipment]))
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.put("/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: int,
    room_data: RoomUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    for key, value in room_data.dict(exclude_unset=True).items():
        setattr(room, key, value)
    
    await db.commit()
    await db.refresh(room)
    return room

@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    await db.delete(room)
    await db.commit()