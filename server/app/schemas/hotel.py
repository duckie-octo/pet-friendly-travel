from pydantic import BaseModel


class PetFriendlyHotel(BaseModel):
    Hotel_Code: int
    Hotel_Name: str
    Address: str | None = None
    City: str
    Zip_Code: str | None = None
    Country: str
    Email: str | None = None
    Phone_Number: str | None = None
    Pet_Friendly: bool
    Pet_Fee_Per_Night: float | None = None
    Max_Pets: int | None = None


class PetFriendlyHotelsResponse(BaseModel):
    Count: int
    Hotels: list[PetFriendlyHotel]
