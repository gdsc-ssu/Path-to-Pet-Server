import database.dbinfo as dbinfo

from fastapi import FastAPI, HTTPException, Depends

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, desc

from datetime import datetime, timedelta

from domain.entity import Animal

from ai.ai import search_similar_images
from domain.gcs import upload_file, delete_file

GCS_BUCKET_NAME = 'path_to_pet_bucket'

# MySQL 연결 정보 설정
db_url = f"mysql+pymysql://{dbinfo.db_username}:{dbinfo.db_password}@{dbinfo.db_host}:{dbinfo.db_port}/{dbinfo.db_name}"
# db_url = f"mysql+pymysql://myggona:ggona12@localhost:3306/path_to_pet"

# SQLAlchemy 엔진 생성
engine = create_engine(db_url)

# 세션 생성
Session = sessionmaker(bind=engine)
session = Session()

page_size = 3


def search_animals(photo, breed, is_dog):
    photo_url = upload_file(photo, breed, is_dog, is_searching=True)
    similar_images = search_similar_images(photo_url, is_dog)
    # similar_images = (3, 4, 8)

    if not similar_images:
        raise HTTPException(status_code=404, detail="No similar images found")

    similar_images = [f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{image}"for image, _ in similar_images]

    # 사진 이름으로 검색하기
    query = session.query(Animal).filter(Animal.photo_url.in_(similar_images))

    animals = query.all()

    return animals


# null은 모두 검색
# term은 n주
def get_animals(page, term, breed, gender, is_neutered, is_adopted, is_dog):
    query = session.query(Animal)

    current_date = datetime.now()
    if term:
        query = query.filter(Animal.admission_date >= current_date - timedelta(weeks=term))

    if breed:
        query = query.filter(Animal.breed == breed)

    if gender:
        query = query.filter(Animal.gender == gender)

    if is_neutered is not None:
        query = query.filter(Animal.is_neutered == is_neutered)

    if is_adopted is not None:
        query = query.filter(Animal.is_adopted == is_adopted)

    if is_dog is not None:
        query = query.filter(Animal.is_dog == is_dog)

    query = query.order_by(desc(Animal.admission_date))

    animals = query.offset((page - 1) * page_size).limit(page_size).all()

    return animals


# 사진 직접 받도록 수정
def create_animals(
        breed,
        gender,
        is_neutered,
        name,
        shelter_location,
        shelter_contact,
        location,
        notes,
        is_adopted,
        is_dog,
        password,
        photo
):
    photo_url = upload_file(photo, breed, is_dog)
    # photo_url = "test_url"

    db_animal = Animal(
        admission_date=datetime.now(),
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
        photo_url=photo_url,
    )

    session.add(db_animal)

    try:
        session.commit()
    except:
        session.rollback()
        raise HTTPException(status_code=500, detail="Unexpected db error")

    return db_animal


def update_animal(
        animal_id,
        breed,
        gender,
        is_neutered,
        name,
        shelter_location,
        shelter_contact,
        location,
        notes,
        is_adopted,
        is_dog,
        password,
        photo
):
    db_animal = session.query(Animal).filter(Animal.id == animal_id).first()

    if db_animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")

    if password != db_animal.password:
        raise HTTPException(status_code=403, detail="Password is incorrect")

    if breed:
        db_animal.breed = breed
    if gender:
        db_animal.gender = gender
    if is_neutered:
        db_animal.is_neutered = is_neutered
    if name:
        db_animal.name = name
    if shelter_location:
        db_animal.shelter_location = shelter_location
    if shelter_contact:
        db_animal.shelter_contact = shelter_contact
    if location:
        db_animal.location = location
    if notes:
        db_animal.notes = notes
    if is_adopted:
        db_animal.is_adopted = is_adopted
    if is_dog:
        db_animal.is_dog = is_dog

    if photo:
        delete_file(db_animal.photo_url)
        photo_url = upload_file(photo, breed, is_dog)
        # photo_url = "test_url"
        db_animal.photo_url = photo_url

    try:
        session.commit()
        session.refresh(db_animal)
    except:
        session.rollback()
        raise HTTPException(status_code=500, detail="Unexpected db error")

    return db_animal


def update_adopted_status(animal_id: int, is_adopted: bool, password: str):
    db_animal = session.query(Animal).filter(Animal.id == animal_id).first()

    if db_animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")

    if password != db_animal.password:
        raise HTTPException(status_code=403, detail="Password is incorrect")

    db_animal.is_adopted = is_adopted

    try:
        session.commit()
        session.refresh(db_animal)
    except:
        session.rollback()
        raise HTTPException(status_code=500, detail="Unexpected db error")

    return db_animal


def delete_animal(animal_id: int, password: str):
    db_animal = session.query(Animal).filter(Animal.id == animal_id).first()

    if db_animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")

    if password != db_animal.password:
        raise HTTPException(status_code=403, detail="Password is incorrect")

    session.delete(db_animal)

    try:
        session.commit()
    except:
        session.rollback()
        raise HTTPException(status_code=500, detail="Unexpected db error")

    delete_file(db_animal.photo_url)

    return db_animal
