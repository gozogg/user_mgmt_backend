
-- schema.sql
-- Single source of truth for all database tables in this project.

CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    business_name VARCHAR(50) NOT NULL,
    default_start_date DATE,
    default_end_date DATE,
    alert_days INTEGER DEFAULT 14,
    alert_email VARCHAR(50)
);

CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    address VARCHAR,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone_number VARCHAR(20),
    email VARCHAR(50),
    city VARCHAR(100),
    latitude DECIMAL,
    longitude DECIMAL,
    postal_code DECIMAL
);

CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    frequency VARCHAR(50) NOT NULL
        CHECK (frequency IN ('weekly', 'biweekly', 'onetime')),
    status VARCHAR(50) DEFAULT 'active'
        CHECK (status IN ('active', 'completed', 'future', 'cancelled', 'past_due')),
    description TEXT NOT NULL,
    day_of_week VARCHAR(50),
    price DECIMAL,
    start_date DATE,
    end_date DATE
);

CREATE TABLE job_dates (
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'not_complete'
        CHECK (status IN ('not_complete', 'complete', 'invoiced')),
    PRIMARY KEY(job_id, date),
    stop_order INTEGER
);

CREATE INDEX clients_organization_id_idx ON clients (organization_id);
CREATE INDEX jobs_organization_id_idx ON jobs (organization_id);
CREATE INDEX job_dates_organization_id_idx ON job_dates (organization_id);
CREATE INDEX job_dates_date_idx ON job_dates (date);
