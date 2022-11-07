CREATE TABLE users (handle text, first_name text, last_name text, rating integer, max_rating integer, user_rank text, max_user_rank text);
CREATE TABLE contests (id integer, difficulty integer);
CREATE TABLE problems (contest_id integer, name text, rating integer, tags text, solved_count integer);
