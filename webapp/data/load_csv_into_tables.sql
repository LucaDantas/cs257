\copy users FROM 'users.csv' DELIMITER ',' CSV QUOTE '"';
\copy contests FROM 'contests.csv' DELIMITER ',' CSV QUOTE '"';
\copy problems FROM 'problems.csv' DELIMITER ',' CSV QUOTE '"';
\copy tags FROM 'tags.csv' DELIMITER ',' CSV QUOTE '"';
\copy problem_tags FROM 'problem_tags.csv' DELIMITER ',' CSV QUOTE '"';
