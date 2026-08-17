
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
        CHECK (frequency IN ('weekly', 'biweekly', 'onetime')),
    description TEXT NOT NULL,
    day_of_week VARCHAR(50),
    price DECIMAL,
    start_date DATE,
    end_date DATE
);


CREATE TABLE job_dates (
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    PRIMARY KEY(job_id, date)
);

CREATE INDEX job_dates_date_idx ON job_dates (date);