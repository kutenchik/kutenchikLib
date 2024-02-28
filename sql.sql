CREATE TABLE IF NOT EXISTS users(
    ID SERIAL PRIMARY KEY,
    USERNAME TEXT,
    PASSWORD TEXT,
    EMAIL TEXT,
    profile_pic text,
    description text default 'Пусто',
	STATUS TEXT DEFAULT 'Участник',
	exp int default 0
);
CREATE TABLE IF NOT EXISTS TITLES(
    TITLE_ID SERIAL PRIMARY KEY,
    NAME_ON_ENGLISH TEXT,
    NAME_ON_RUSSIAN TEXT,
    DESCRIPTION TEXT,
    YEAR INT,
    COVER TEXT, 
    GENRES TEXT,
    amount_of_views int DEFAULT 0,
	TYPE TEXT DEFAULT 'манга'
);
CREATE TABLE IF NOT EXISTS GLAVA(
    TITLE_ID INT,
    nomer_glavi int,
    GLAVA TEXT,
    IMAGES TEXT,
	last_update TIMESTAMP DEFAULT date_trunc('minute', NOW()),
    FOREIGN KEY(TITLE_ID) REFERENCES TITLES(TITLE_ID) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS COMMENTS(
	COMMENT_ID SERIAL PRIMARY KEY,
	TITLE_NAME INT,
	NOMER_GLAVI INT,
	USER_ID INT,
	COMMENT_TEXT TEXT,
	COMMENT_DATE TEXT,
	FOREIGN KEY(USER_ID) REFERENCES USERS(ID)
);
create table if not exists favourites(
	user_id int,
	title_id int,
	foreign key (user_id) references users(id),
	foreign key (title_id) references titles(title_id) ON DELETE CASCADE
);
create table if not exists user_ratings(
	user_id int,
	title_id int,
	rating float,
	foreign key (user_id) references users(id),
	foreign key (title_id) references titles(title_id) ON DELETE CASCADE
);
create table if not exists user_reading_history(
	user_id int,
	title_id int,
	last_chapter_read int,
	foreign key (user_id) references users(id),
	foreign key (title_id) references titles(title_id) ON DELETE CASCADE
);
create table if not exists user_chapter_status(
	user_id int,
	title_id int,
	nomer_glavi int,
	is_read bool,
	foreign key (user_id) references users(id),
	foreign key (title_id) references titles(title_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS ACHIEVEMENTS(
	ACHIEVEMENT_ID SERIAL PRIMARY KEY,
	ACHIEVEMNT_NAME TEXT,
	ACHIEVEMENT_DESC TEXT,
	achievement_image text
);
CREATE TABLE IF NOT EXISTS USER_ACHIEVEMENTS(
	ACHIEVEMENT_ID INT,
	USER_ID INT,
	FOREIGN KEY(ACHIEVEMENT_ID) REFERENCES ACHIEVEMENTS(ACHIEVEMENT_ID),
	FOREIGN KEY(USER_ID) REFERENCES USERS(ID)
);
CREATE TABLE IF NOT EXISTS USERS_FULL_TITLE_READ(
	TITLE_ID INT,
	USER_ID INT,
	FOREIGN KEY(TITLE_ID) REFERENCES TITLES(TITLE_ID),
	FOREIGN KEY(USER_ID) REFERENCES USERS(ID)
);
CREATE TABLE IF NOT EXISTS RANOBE_GLAVI(
	TITLE_ID INT,
    nomer_glavi int,
    GLAVA TEXT,
    CONTENT_GLAVI text[],
	last_update TIMESTAMP DEFAULT date_trunc('minute', NOW()),
    FOREIGN KEY(TITLE_ID) REFERENCES TITLES(TITLE_ID) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS ANIME_SERII(
	TITLE_ID INT,
    nomer_glavi int,
    GLAVA TEXT,
    html_code text,
	last_update TIMESTAMP DEFAULT date_trunc('minute', NOW()),
    FOREIGN KEY(TITLE_ID) REFERENCES TITLES(TITLE_ID) ON DELETE CASCADE
);
CREATE VIEW IF NOT EXISTS titles_for_zapros AS SELECT DISTINCT NAME_ON_RUSSIAN,cover,name_on_english,genres,amount_of_views,COALESCE(manga.glava_count, 0) + COALESCE(ranobe.glava_count, 0) + COALESCE(anime.glava_count, 0) AS glava_count,year,description,AVG(rating) OVER(PARTITION BY title_id) AS average_rating,type
FROM TITLES
LEFT JOIN (
    SELECT TITLE_ID, COUNT(*) AS glava_count
    FROM GLAVA
    GROUP BY TITLE_ID
) AS manga USING(TITLE_ID)
LEFT JOIN (
    SELECT TITLE_ID, COUNT(*) AS glava_count
    FROM RANOBE_GLAVI
    GROUP BY TITLE_ID
)AS ranobe USING(TITLE_ID)
LEFT JOIN (
	SELECT TITLE_ID, COUNT(*) AS glava_count
    FROM ANIME_SERII
    GROUP BY TITLE_ID
)AS ANIME USING(TITLE_ID)
LEFT JOIN user_ratings USING(TITLE_ID);

CREATE INDEX IF NOT EXISTS idx_comments_user_id ON COMMENTS (USER_ID);
CREATE INDEX IF NOT EXISTS idx_comments_title_name ON COMMENTS (TITLE_NAME);
CREATE INDEX IF NOT EXISTS idx_comments_nomer_glavi ON COMMENTS (NOMER_GLAVI);


CREATE INDEX IF NOT EXISTS idx_anime_serii_title_id ON ANIME_SERII (TITLE_ID);
CREATE INDEX IF NOT EXISTS idx_anime_serii_nomer_glavi ON ANIME_SERII (nomer_glavi);


CREATE INDEX IF NOT EXISTS idx_users_full_title_read_title_id ON USERS_FULL_TITLE_READ (TITLE_ID);
CREATE INDEX IF NOT EXISTS idx_users_full_title_read_user_id ON USERS_FULL_TITLE_READ (USER_ID);


CREATE INDEX IF NOT EXISTS idx_user_achievements_achievement_id ON USER_ACHIEVEMENTS (ACHIEVEMENT_ID);
CREATE INDEX IF NOT EXISTS idx_user_achievements_user_id ON USER_ACHIEVEMENTS (USER_ID);



CREATE INDEX IF NOT EXISTS idx_user_chapter_status_user_id ON user_chapter_status (user_id);
CREATE INDEX IF NOT EXISTS idx_user_chapter_status_title_id ON user_chapter_status (title_id);
CREATE INDEX IF NOT EXISTS idx_user_chapter_status_nomer_glavi ON user_chapter_status (nomer_glavi);
CREATE INDEX IF NOT EXISTS idx_user_chapter_status_is_read ON user_chapter_status (is_read);


CREATE INDEX IF NOT EXISTS idx_user_reading_history_user_id ON user_reading_history (user_id);
CREATE INDEX IF NOT EXISTS idx_user_reading_history_title_id ON user_reading_history (title_id);
CREATE INDEX IF NOT EXISTS idx_user_reading_history_last_chapter_read ON user_reading_history (last_chapter_read);



CREATE INDEX IF NOT EXISTS idx_user_ratings_user_id ON user_ratings (user_id);
CREATE INDEX IF NOT EXISTS idx_user_ratings_title_id ON user_ratings (title_id);
CREATE INDEX IF NOT EXISTS idx_user_ratings_rating ON user_ratings (rating);


CREATE INDEX IF NOT EXISTS idx_favourites_user_id ON favourites (user_id);
CREATE INDEX IF NOT EXISTS idx_favourites_title_id ON favourites (title_id);


CREATE INDEX IF NOT EXISTS idx_glava_title_id ON GLAVA (TITLE_ID);
CREATE INDEX IF NOT EXISTS idx_glava_nomer_glavi ON GLAVA (nomer_glavi);


CREATE INDEX IF NOT EXISTS idx_titles_title_id ON TITLES (TITLE_ID);
CREATE INDEX IF NOT EXISTS idx_titles_name_english ON TITLES (NAME_ON_ENGLISH);
CREATE INDEX IF NOT EXISTS idx_titles_name_russian ON TITLES (NAME_ON_RUSSIAN);
CREATE INDEX IF NOT EXISTS idx_titles_year ON TITLES (YEAR);
CREATE INDEX IF NOT EXISTS idx_titles_genres ON TITLES (GENRES);
CREATE INDEX IF NOT EXISTS idx_titles_type ON TITLES (TYPE);
