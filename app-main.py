from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import create_tables
from app.routers import auth, rooms, bookings, availability

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(
    title="Sirius.Rent API",
    description="Сервис бронирования пространств",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(bookings.router)
app.include_router(availability.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def root():
    return {
        "message": "Sirius.Rent API",
        "docs": "/docs",
        "redoc": "/redoc"
    }