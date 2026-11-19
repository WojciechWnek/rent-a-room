from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.booking import Booking


# base model class - shared fields for all HTTP
class RoomBase(SQLModel):
    name: str = Field()
    price_per_night: int = Field()
    bedrooms: float = Field(multiple_of=0.5)
    bathrooms: float = Field(multiple_of=0.5)


# Room table model - map to the "rooms" databes model
class Room(RoomBase, table=True):
    __tablename__: str = "rooms"

    id: int | None = Field(default=None, primary_key=True)

    bookings: list["Booking"] = Relationship(
        back_populates="room", passive_deletes="all"
    )


# room response model
class RoomPublic(RoomBase):
    id: int


# all filedls can be optional fileds for update
class RoomUpdate(SQLModel):
    name: str | None = None
    price_per_night: int | None = None
    bedrooms: float | None = None
    bathrooms: float | None = None


class RoomWithCount(RoomPublic):
    booking_count: int
