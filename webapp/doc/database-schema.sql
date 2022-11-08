CREATE TABLE users (handle text, first_name text, last_name text, country text, organization text, rating integer, max_rating integer, user_rank text, max_user_rank text);
CREATE TABLE contests (id integer, total_solves integer);
CREATE TABLE problems (problem_id integer, contest_id integer, name text, idx text, rating integer, solved_count integer);
CREATE TABLE tags (id SERIAL, name text);
CREATE TABLE problem_tags (problem_id integer, tag_id integer);
