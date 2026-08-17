
-- schema.sql
-- Single source of truth for all database tables in this project.
 

CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    address VARCHAR,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone_number VARCHAR(20),
    email VARCHAR(50)
);

CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id),
    frequency VARCHAR(50) NOT NULL
        CHECK (frequency IN ('weekly', 'biweekly', 'one time')),
    description TEXT NOT NULL,
    day_of_week VARCHAR(50),
    price DECIMAL
);

CREATE TABLE dates (
    date DATE PRIMARY KEY,
    total_profit DECIMAL
)

CREATE TABLE job_dates (
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    date DATE NOT NULL REFERENCES dates(date) ON DELETE CASCADE,
    PRIMARY KEY(job_id, dates)
)