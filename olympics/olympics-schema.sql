CREATE TABLE olympiad (
    id SERIAL,
    games text,
    year integer,
    season text,
    city text
);

CREATE TABLE noc_reg (
    id SERIAL,
    noc text,
    team text,
    notes text
);

CREATE TABLE athlete (
    id SERIAL,
    name text,
    sex text
);

CREATE TABLE athlete_year (
    id SERIAL,
    olympiad_id integer,
    athlete_id integer,
    noc_reg_id integer,
    age integer,
    height integer,
    weight real
);

CREATE TABLE event (
    id SERIAL,
    event text,
    sport text
);

CREATE TABLE medal (
    id SERIAL,
    athlete_year_id integer,
    event_id integer,
    medal text
);
