-- create schema

-- episodes table
CREATE TABLE episodes
(
    episode_id  SERIAL PRIMARY KEY,
    title       TEXT,
    url         TEXT,
    guest_stars TEXT,
    synopsis    TEXT

);

-- dialogue table
CREATE TABLE dialogue
(
    dialogue_id SERIAL PRIMARY KEY,
    episode_id  INTEGER REFERENCES episodes (episode_id) ON DELETE CASCADE,
    speaker     TEXT,
    text        TEXT,
    actions     TEXT
);

-- tokens table
CREATE TABLE tokens
(
    token_id    SERIAL PRIMARY KEY,
    dialogue_id INTEGER REFERENCES dialogue (dialogue_id) ON DELETE CASCADE,
    token       TEXT,
    token_type  TEXT
);

-- actions table
CREATE TABLE actions
(
    action_id          SERIAL PRIMARY KEY,
    dialogue_id        INTEGER REFERENCES dialogue (dialogue_id) ON DELETE CASCADE,
    action_type        TEXT,
    action_description TEXT
);

-- Optional Text Search Index
CREATE INDEX dialogue_text_idx ON dialogue USING GIN (text);
