-- 1. CREATE TABLE
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    degree INTEGER NOT NULL,
    class_name VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    class_name VARCHAR
);

CREATE TABLE IF NOT EXISTS spreadsheets (
    id SERIAL PRIMARY KEY,
    degree INTEGER NOT NULL,
    url VARCHAR NOT NULL,
    sheet_name VARCHAR
);

-- 2. INSERT INTO groups
INSERT INTO groups (id, degree, class_name) VALUES
(1, 4, '22-302 SW'),
(2, 4, '22-303 SW'),
(3, 4, '22-301 SW'),
(4, 4, '22-304 DA'),
(5, 4, '22-305 AI'),
(6, 4, '22-306 AI'),
(7, 4, '22-307 BA'),
(8, 3, '23-301 DA'),
(9, 3, '23-302 DA'),
(10, 3, '23-303 AI'),
(11, 3, '23-304 AI'),
(12, 3, '23-305 AI'),
(13, 3, '23-306 BA'),
(14, 3, '23-307 BA'),
(15, 3, '23-308 SW'),
(16, 3, '23-309 SW'),
(17, 3, '23-310 SW'),
(18, 3, '23-311 SW'),
(19, 3, '23-312 SW'),
(20, 3, '23-313 SW'),
(21, 3, '23-314 SW'),
(22, 3, '23-315 SW'),
(23, 3, '23-316 SW'),
(24, 2, '24-301 DA'),
(25, 2, '24-302 AI'),
(26, 2, '24-303 C#'),
(27, 2, '24-304 Python'),
(28, 2, '24-401 DA'),
(29, 2, '24-402 DA'),
(30, 2, '24-403 AI'),
(31, 2, '24-404 BA'),
(32, 2, '24-405 BA'),
(33, 2, '24-406 Java'),
(34, 2, '24-407 Java'),
(35, 2, '24-408 C#'),
(36, 2, '24-409 Python'),
(37, 2, '24-411 Python'),
(38, 2, '24-412 Frontend'),
(39, 2, '24-413 Frontend'),
(40, 2, '24-414 Flutter');

-- 3. INSERT INTO users
INSERT INTO users (id, chat_id, class_name) VALUES
(2, 1985601122, '22-302 SW'),
(1, 1059249931, '22-302 SW');

-- 4. INSERT INTO spreadsheets
INSERT INTO spreadsheets (id, degree, url, sheet_name) VALUES
(1, 4, 'https://docs.google.com/spreadsheets/d/1Pi8qbrMfS4i5MbarSDzbDszVC0pZNEtLsI4XuDvOHqg/edit?gid=1170996177#gid=1170996177', 'Time Table 4th course 7th semestr V2'),
(2, 3, 'https://docs.google.com/spreadsheets/d/1gH9oaXa1F3S9-fX-Lq_fQNSbwJ-njXVG6bg-HQ2C6xY/edit?gid=1103642390#gid=1103642390', 'Time Table 3rd course 5th semestr V2'),
(3, 2, 'https://docs.google.com/spreadsheets/d/1Xu3Pl5zAXnLGG2miTyV4Yk3pOQwmSa0jcSIVQXuKbOA/edit?gid=392765863#gid=392765863', 'Time Table 2nd Course 3rd semestr V2');
