-- Trips database (Render: Pet_friendly_travel)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS airlines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    iata_code VARCHAR(8) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    country_code VARCHAR(2),
    logo_url VARCHAR(2048),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS airline_pet_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    airline_id UUID NOT NULL UNIQUE REFERENCES airlines(id) ON DELETE CASCADE,
    allow_pet BOOLEAN NOT NULL DEFAULT TRUE,
    fee_currency VARCHAR(8),
    policy_source_url VARCHAR(2048),
    policy_version VARCHAR(64),
    updated_by UUID,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS flights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_flight_id VARCHAR(255),
    booking_search_id VARCHAR(255),
    airline_id UUID NOT NULL REFERENCES airlines(id),
    flight_number VARCHAR(32) NOT NULL,
    origin_iata VARCHAR(8) NOT NULL,
    destination_iata VARCHAR(8) NOT NULL,
    departs_at TIMESTAMPTZ NOT NULL,
    arrives_at TIMESTAMPTZ NOT NULL,
    duration_minutes INTEGER,
    stops INTEGER NOT NULL DEFAULT 0,
    price NUMERIC(12, 2),
    cabin_class VARCHAR(32),
    currency VARCHAR(8),
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    cache_expires_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS hotels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_hotel_id VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(512) NOT NULL,
    address VARCHAR(512),
    city VARCHAR(128) NOT NULL,
    country_code VARCHAR(8) NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    star_rating INTEGER,
    review_score DOUBLE PRECISION,
    price_per_night NUMERIC(12, 2),
    currency VARCHAR(8),
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    cache_expires_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS hotel_dog_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hotel_id UUID NOT NULL UNIQUE REFERENCES hotels(id) ON DELETE CASCADE,
    dogs_allowed BOOLEAN NOT NULL DEFAULT TRUE,
    size_allowed VARCHAR(128),
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    admin_updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS pet_places (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    google_place_id VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(512) NOT NULL,
    address VARCHAR(512),
    city VARCHAR(128),
    country_code VARCHAR(8),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    pet_category VARCHAR(128),
    pet_subcategory VARCHAR(128),
    google_rating DOUBLE PRECISION,
    review_count INTEGER,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    cache_expires_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS pet_place_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pet_place_id UUID NOT NULL UNIQUE REFERENCES pet_places(id) ON DELETE CASCADE,
    accepts_dogs BOOLEAN NOT NULL DEFAULT TRUE,
    size_restrictions VARCHAR(255),
    breed_restrictions VARCHAR(255),
    fee_info VARCHAR(255),
    amenities TEXT,
    opening_hours TEXT,
    website_url VARCHAR(2048),
    updated_by UUID,
    admin_updated_at TIMESTAMPTZ,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'planned',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trips_user_id ON trips(user_id);

CREATE TABLE IF NOT EXISTS trip_flights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    flight_id UUID NOT NULL REFERENCES flights(id),
    sort_order INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trip_hotels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    hotel_id UUID NOT NULL REFERENCES hotels(id),
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    guests INTEGER NOT NULL DEFAULT 1,
    notes TEXT,
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trip_pet_places (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    pet_place_id UUID NOT NULL REFERENCES pet_places(id),
    sort_order INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
