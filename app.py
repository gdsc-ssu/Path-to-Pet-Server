from fastapi import FastAPI, UploadFile, File, Form
from typing import Optional, List, Union
from pydantic import BaseModel
import uvicorn

from datetime import datetime

from domain.animals import search_animals, get_animals, create_animals, delete_animal, update_animal, update_adopted_status
from domain.entity import Animal, AnimalBreed

app = FastAPI()

class AnimalBase(BaseModel):
    id: int
    admission_date: datetime
    breed: Optional[AnimalBreed]
    gender: Optional[str]
    is_neutered: Optional[bool]
    name: Optional[str]
    shelter_location: Optional[str]
    shelter_contact: Optional[str]
    location: Optional[str]
    notes: Optional[str]
    photo_url: Optional[str]
    is_adopted: bool
    is_dog: bool
    password: str

    class Config:
        orm_mode = True

class UpdateAnimalAdoptedRequest(BaseModel):
    is_adopted: bool
    password: str

class DeleteAnimalRequest(BaseModel):
    password: str

@app.get("/animals/image", response_model=List[AnimalBase])
def search_and_page_animals(
    is_dog: bool = Form(...),
    photo: UploadFile = File(...)
):
    return search_animals(photo=photo, is_dog=is_dog)

@app.get("/animals", response_model=List[AnimalBase])
def page_animals(
    page: int = 1,
    term: int = 0,
    breed: AnimalBreed = None,
    gender: str = None,
    is_neutered: bool = None,
    is_adopted: bool = None,
    is_dog: bool = None
):
    return get_animals(page=page, term=term, breed=breed, gender=gender, is_neutered=is_neutered, is_adopted=is_adopted, is_dog=is_dog)

@app.post("/animals/", response_model=AnimalBase)
def add_animal(
    breed: AnimalBreed = Form(...),
    gender: str = Form(...),
    is_neutered: bool = Form(...),
    name: str = Form(...),
    shelter_location: str = Form(...),
    shelter_contact: str = Form(...),
    location: str = Form(...),
    notes: str = Form(...),
    is_adopted: bool = Form(...),
    is_dog: bool = Form(...),
    password: str = Form(...),
    photo: UploadFile = File(...)
):
    return create_animals(
        breed=breed,
        gender=gender,
        is_neutered=is_neutered,
        name=name,
        shelter_location=shelter_location,
        shelter_contact=shelter_contact,
        location=location,
        notes=notes,
        is_adopted=is_adopted,
        is_dog=is_dog,
        password=password,
        photo=photo
    )

@app.put("/animals/{animal_id}", response_model=AnimalBase)
def fix_animal(
    animal_id: int,
    breed: Union[AnimalBreed, None] = Form(None),
    gender: Union[str, None] = Form(None),
    is_neutered: Union[bool, None] = Form(None),
    name: Union[str, None] = Form(None),
    shelter_location: Union[str, None] = Form(None),
    shelter_contact: Union[str, None] = Form(None),
    location: Union[str, None] = Form(None),
    notes: Union[str, None] = Form(None),
    is_adopted: Union[bool, None] = Form(None),
    is_dog: Union[bool, None] = Form(None),
    password: str = Form(None),
    photo: Union[bytes, None] = None,
):
    return update_animal(
        animal_id=animal_id,
        breed=breed,
        gender=gender,
        is_neutered=is_neutered,
        name=name,
        shelter_location=shelter_location,
        shelter_contact=shelter_contact,
        location=location,
        notes=notes,
        is_adopted=is_adopted,
        is_dog=is_dog,
        password=password,
        photo=photo
    )

@app.put("/animals/{animal_id}/adopted")
def fix_animal(animal_id: int, request_data: UpdateAnimalAdoptedRequest):
    update_adopted_status(animal_id, request_data.is_adopted, request_data.password)

@app.delete("/animals/{animal_id}")
def remove_animal(animal_id: int, request_data: DeleteAnimalRequest):
    delete_animal(animal_id, request_data.password)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)