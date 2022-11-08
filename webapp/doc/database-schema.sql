CREATE TABLE users (handle text, first_name text, last_name text, country text, organization text, rating integer, max_rating integer, user_rank text, max_user_rank text);
CREATE TABLE contests (id integer, total_solves integer, difficulty integer);
CREATE TABLE problems (problem_id text, contest_id integer, name text, rating integer, solved_count integer);
CREATE TABLE tags (id SERIAL, name text);
CREATE TABLE problem_tags (problem_id text, tag_id integer);
