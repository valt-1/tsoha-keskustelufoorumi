CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    subject TEXT
);
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    content TEXT,
    sent_at TIMESTAMP,
    visible INTEGER,
    topic_id INTEGER REFERENCES topics
);
