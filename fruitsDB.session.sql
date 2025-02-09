CREATE TABLE places (
    id SERIAL PRIMARY KEY,
    place_name VARCHAR(80) NOT NULL,
    country VARCHAR(100) NOT NULL
);

CREATE TABLE ways_to_get (
    id SERIAL PRIMARY KEY,
    method VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);


CREATE TABLE fruits (
    id SERIAL PRIMARY KEY,
    official_name VARCHAR(50) NOT NULL,
    other_name VARCHAR(50) NULL,
    scientific_name VARCHAR(80),
    cultivar VARCHAR(255),
    other_links TEXT,
    image_url TEXT,
    special_condition TEXT,
    tried_date DATE,
    place_id INT REFERENCES places(id) ON DELETE SET NULL, 
    way_id INT REFERENCES ways_to_get(id) ON DELETE SET NULL 
);



CREATE TABLE fruit_reviews (
    id SERIAL PRIMARY KEY,
    fruit_id INT REFERENCES fruits(id) ON DELETE CASCADE,
    taste_score INT CHECK (taste_score BETWEEN 0 AND 10),
    experience_score INT CHECK (experience_score BETWEEN 0 AND 10),
    review TEXT
);



CREATE TABLE fruits_users (
    id SERIAL PRIMARY KEY,
    fruit_id INT REFERENCES fruits(id) ON DELETE CASCADE,
    user_id INT REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE fruit_videos (
    id SERIAL PRIMARY KEY,
    fruit_id INT REFERENCES fruits(id) ON DELETE CASCADE,
    description TEXT,
    video_link TEXT
);