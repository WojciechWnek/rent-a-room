from contextlib import asynccontextmanager
from typing import Annotated, Literal

from fastapi import Cookie, FastAPI, Header, HTTPException, Query, Response, status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, StringConstraints, field_validator
from sqlmodel import col, func, select

from database import SessionDep, create_db_and_tables
from models import Room

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
app.mount("/assets", StaticFiles(directory="assets"), name="assets")


class RoomQueryParams(BaseModel):
    max_price: int | None = Field(
        default=None, ge=10, le=10_000, examples=[100, 200, 10_000]
    )
    search: Annotated[str | None, StringConstraints(to_lower=True)] = Field(
        default=None,
        min_length=3,
        max_length=10,
        title="Search term",
        description="Provide a keyword to search within room title",
        examples=["sunny", "cozy"],
    )
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

    @field_validator("search")
    @classmethod
    def fail_if_funny(cls, search: str) -> str:
        if "lol" in search:
            raise ValueError("No funny business allowed")
        return search


class AppCookies(BaseModel):
    theme: Literal["light", "dark"] = "dark"
    language: Literal["en", "es", "pl"] = "en"


class AppHeaders(BaseModel):
    user_agent: str | None


@app.get("/", status_code=status.HTTP_200_OK)
def root(
    app_cookies: Annotated[AppCookies, Cookie()],
    app_headers: Annotated[AppHeaders, Header()],
):
    greetings = {
        "en": "Welcome to Rent a Room",
        "es": "Bienvienidos a Rent a Room",
        "pl": "Witamy w Rent a Room",
    }
    greeting = greetings.get(app_cookies.language)
    return {"message": greeting, "user_agent": app_headers.user_agent}


@app.post("/rooms", status_code=status.HTTP_201_CREATED, tags=["rooms"])
def create_room(session: SessionDep, room: Room) -> Room:
    session.add(room)
    session.commit()
    session.refresh(room)
    return room


@app.get(
    "/rooms",
    status_code=status.HTTP_200_OK,
    tags=["rooms"],
    summary="List all avaliable rooms",
    description="Returns all rooms. Supports filtering",
    response_description="A list of rooms matching the filter criteria",
)
def get_rooms(session: SessionDep, params: Annotated[RoomQueryParams, Query()]):
    statement = select(Room)

    if params.max_price:
        statement = statement.where(Room.price_per_night <= params.max_price)

    if params.search:
        # statement = statement.where(func.lower(Room.name).contains(params.search))
        statement = statement.where(col(Room.name).like(f"%{params.search}%"))

    statement = (
        statement.limit(params.limit).offset(params.offset).order_by(col(Room.id))
    )

    return session.exec(statement).all()


@app.get("/rooms/{room_id}", status_code=status.HTTP_200_OK, tags=["rooms"])
def get_room(room_id: int):
    for room in [apartment, house, studio]:
        if room["id"] == room_id:
            return room

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")


@app.get("/preferences", status_code=status.HTTP_200_OK, tags=["preferences"])
def set_preferences(response: Response):

    app_cookies = AppCookies()

    response.set_cookie(key="theme", value=app_cookies.theme)
    response.set_cookie(key="language", value=app_cookies.languageß)
    return {"message": "Preferences set"}
