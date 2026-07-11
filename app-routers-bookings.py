from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, date
from typing import List
from app.database import get_db
from app.models import Booking, BookingStatus, Room, User
from app.schemas import BookingCreate, BookingResponse
from app.dependencies import get_current_active_user
from app.utils.validators import is_room_available

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Room).where(Room.id == booking_data.room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if not await is_room_available(booking_data.room_id, booking_data.start_time, booking_data.end_time, db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Room is already booked for the selected time"
        )
    
    new_booking = Booking(
        room_id=booking_data.room_id,
        user_id=current_user.id,
        start_time=booking_data.start_time,
        end_time=booking_data.end_time
    )
    db.add(new_booking)
    await db.commit()
    await db.refresh(new_booking)
    return new_booking

@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own bookings"
        )
    
    booking.status = BookingStatus.CANCELLED
    await db.commit()

@router.get("/rooms/{room_id}/bookings", response_model=List[BookingResponse])
async def get_room_bookings(
    room_id: int,
    date: date = Query(..., description="Date in YYYY-MM-DD format"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    result = await db.execute(select(Room).where(Room.id == room_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Room not found")
    
    start_of_day = datetime.combine(date, datetime.min.time())
    end_of_day = datetime.combine(date, datetime.max.time())
    
    query = select(Booking).where(
        Booking.room_id == room_id,
        Booking.status == BookingStatus.ACTIVE,
        Booking.start_time >= start_of_day,
        Booking.start_time <= end_of_day
    ).order_by(Booking.start_time)
    
    result = await db.execute(query)
    return result.scalars().all()