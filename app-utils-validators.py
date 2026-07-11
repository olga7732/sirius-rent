from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.models import Booking, BookingStatus

async def is_room_available(
    room_id: int,
    start_time: datetime,
    end_time: datetime,
    db: AsyncSession,
    exclude_booking_id: Optional[int] = None
) -> bool:
    """Проверяет, свободна ли комната в указанный промежуток времени"""
    query = select(Booking).where(
        Booking.room_id == room_id,
        Booking.status == BookingStatus.ACTIVE,
        Booking.start_time < end_time,
        Booking.end_time > start_time
    )
    if exclude_booking_id:
        query = query.where(Booking.id != exclude_booking_id)
    
    result = await db.execute(query)
    return result.scalar() is None

async def find_available_rooms(
    start_time: datetime,
    end_time: datetime,
    capacity: Optional[int],
    db: AsyncSession
) -> List[int]:
    """Возвращает ID комнат, свободных в указанный промежуток"""
    from app.models import Room
    from sqlalchemy import not_

    busy_query = select(Booking.room_id).where(
        Booking.status == BookingStatus.ACTIVE,
        Booking.start_time < end_time,
        Booking.end_time > start_time
    )
    busy_result = await db.execute(busy_query)
    busy_room_ids = [row[0] for row in busy_result.all()]

    room_query = select(Room)
    if capacity:
        room_query = room_query.where(Room.capacity >= capacity)
    if busy_room_ids:
        room_query = room_query.where(not_(Room.id.in_(busy_room_ids)))
    
    result = await db.execute(room_query)
    return [room.id for room in result.scalars().all()]