
URBANFLOW ANALYTICS - ATHENA SQL QUERIES


QUERY 1: Top 10 Most Delayed Stations
SELECT station, AVG(arrival_delay_m) as avg_delay, COUNT(*) as total_trains
FROM urbanflow_athena_db.delays_view
WHERE arrival_delay_m IS NOT NULL AND arrival_delay_m <= 120
GROUP BY station
HAVING COUNT(*) > 100
ORDER BY avg_delay DESC
LIMIT 10;

QUERY 2: Delay by Hour of Day (Peak Hours)
SELECT hour, AVG(arrival_delay_m) as avg_delay, COUNT(*) as count
FROM urbanflow_athena_db.delays_view
WHERE hour IS NOT NULL AND arrival_delay_m IS NOT NULL
GROUP BY hour
ORDER BY hour;

QUERY 3: Daily Delay Trend
SELECT date, AVG(arrival_delay_m) as avg_delay, COUNT(*) as count
FROM urbanflow_athena_db.delays_view
WHERE date IS NOT NULL AND arrival_delay_m IS NOT NULL
GROUP BY date
ORDER BY date;

QUERY 4: Most Delayed Train Lines
SELECT line, AVG(arrival_delay_m) as avg_delay, COUNT(*) as count
FROM urbanflow_athena_db.delays_view
WHERE line IS NOT NULL AND line != '' AND arrival_delay_m IS NOT NULL
GROUP BY line
HAVING COUNT(*) > 50
ORDER BY avg_delay DESC
LIMIT 10;