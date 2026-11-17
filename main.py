from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.dependencies.database import create_db_and_tables
from app.routers import general, rooms

openapi_tags = [{"name": "rooms", "description": "Operations with **rooms**"}]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # before server starts
    create_db_and_tables()
    yield
    # after server shutdown


app = FastAPI(
    lifespan=lifespan,
    title="Rent a Room API",
    description="Book a stay in a house or room",
    version="1.0.0",
    contact={"name": "Wnek", "email": "wnek@wnek.com"},
    openapi_tags=openapi_tags,
)
app.include_router(general.router)
app.include_router(rooms.router)
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
