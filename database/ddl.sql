CREATE TABLE animals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admission_date DATETIME NOT NULL,
    breed VARCHAR(255),
    gender CHAR(1) CHECK (gender IN ('M', 'F')),
    is_neutered BOOLEAN,
    name VARCHAR(255),
    shelter_location VARCHAR(255),
    shelter_contact VARCHAR(255),
    location VARCHAR(255),
    notes VARCHAR(2048),
    photo_url VARCHAR(2048),
    password VARCHAR(255) not null,
    is_adopted BOOLEAN not null,
    is_dog BOOLEAN not null
);

ALTER TABLE animals
CHANGE COLUMN photo_url photo_url VARCHAR(1024) CHARACTER SET utf8;

ALTER TABLE animals
ADD CONSTRAINT uk_photo_url UNIQUE (photo_url);