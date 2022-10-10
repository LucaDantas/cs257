SELECT * FROM noc_reg
ORDER BY noc_reg.noc;

SELECT DISTINCT athlete.name
FROM athlete, athlete_year, noc_reg
WHERE noc_reg.team = 'Jamaica'
AND noc_reg.id = athlete_year.noc_reg_id
AND athlete_year.athlete_id = athlete.id;

SELECT medal.medal, olympiad.games, event.event, athlete_year.age
FROM olympiad, athlete, athlete_year, medal, event
WHERE athlete.name LIKE '%Louganis%'
AND athlete.id = athlete_year.athlete_id
AND athlete_year.olympiad_id = olympiad.id
AND athlete_year.id = medal.athlete_year_id
AND medal.event_id = event.id;

SELECT noc_reg.noc, COUNT(medal.medal) AS gold_medal_count
FROM noc_reg, athlete_year, medal
WHERE noc_reg.id = athlete_year.noc_reg_id
AND medal.athlete_year_id = athlete_year.id
AND medal.medal = 'Gold'
GROUP BY noc_reg.noc
ORDER BY COUNT(medal.medal) DESC;
