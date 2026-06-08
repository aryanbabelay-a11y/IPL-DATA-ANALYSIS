
CREATE TABLE matches (
    id               INTEGER       PRIMARY KEY,
    season           VARCHAR(10),
    city             VARCHAR(100),
    date             DATE,
    match_type       VARCHAR(50),
    player_of_match  VARCHAR(100),
    venue            VARCHAR(150),
    team1            VARCHAR(100),
    team2            VARCHAR(100),
    toss_winner      VARCHAR(100),
    toss_decision    VARCHAR(10),
    winner           VARCHAR(100),
    result           VARCHAR(20),
    result_margin    INTEGER,          -- nullable (ties / no result)
    target_runs      INTEGER,          -- nullable
    target_overs     INTEGER,          -- nullable
    super_over       CHAR(1),          -- 'Y' or 'N'
    method           VARCHAR(10),      -- 'D/L' or NULL
    umpire1          VARCHAR(100),
    umpire2          VARCHAR(100)
);

SELECT * FROM matches
-- ------------------------------------------------------------
-- 1C. DELIVERIES TABLE
-- ------------------------------------------------------------


CREATE TABLE deliveries (
    id               SERIAL        PRIMARY KEY,   -- surrogate key (not in CSV)
    match_id         INTEGER       NOT NULL REFERENCES matches(id),
    inning           SMALLINT,
    batting_team     VARCHAR(100),
    bowling_team     VARCHAR(100),
    over             SMALLINT,
    ball             SMALLINT,
    batter           VARCHAR(100),
    bowler           VARCHAR(100),
    non_striker      VARCHAR(100),
    batsman_runs     SMALLINT,
    extra_runs       SMALLINT,
    total_runs       SMALLINT,
    extras_type      VARCHAR(20),   -- NULL when no extra
    is_wicket        SMALLINT,      -- 0 or 1
    player_dismissed VARCHAR(100),  -- NULL when no wicket
    dismissal_kind   VARCHAR(50),   -- NULL when no wicket
    fielder          VARCHAR(100)   -- NULL when not applicable
);

### Q1. Top 10 Teams by Total Wins
```sql
SELECT winner AS team, COUNT(*) AS total_wins
FROM matches
WHERE winner IS NOT NULL
GROUP BY winner
ORDER BY total_wins DESC
LIMIT 10;
```

---

### Q2. Toss Win → Match Win Rate by Decision
```sql
SELECT
    toss_decision,
    COUNT(*) AS total_matches,
    SUM(CASE WHEN toss_winner = winner THEN 1 ELSE 0 END) AS toss_and_match_wins,
    ROUND(100.0 * SUM(CASE WHEN toss_winner = winner THEN 1 ELSE 0 END) / COUNT(*), 2) AS win_pct
FROM matches
WHERE winner IS NOT NULL
GROUP BY toss_decision;
```

---

### Q3. Team Win Percentage (min 30 matches)
```sql
WITH all_matches AS (
    SELECT team1 AS team FROM matches
    UNION ALL
    SELECT team2 AS team FROM matches
),
played AS (
    SELECT team, COUNT(*) AS matches_played FROM all_matches GROUP BY team
),
wins AS (
    SELECT winner AS team, COUNT(*) AS matches_won
    FROM matches WHERE winner IS NOT NULL
    GROUP BY winner
)
SELECT
    p.team,
    p.matches_played,
    w.matches_won,
    ROUND(100.0 * w.matches_won / p.matches_played, 2) AS win_pct
FROM played p
JOIN wins w ON p.team = w.team
WHERE p.matches_played >= 30
ORDER BY win_pct DESC;
```

---

### Q4. Top 10 Run Scorers (All Time)
```sql
SELECT batter, SUM(batsman_runs) AS total_runs
FROM deliveries
GROUP BY batter
ORDER BY total_runs DESC
LIMIT 10;
```

---

### Q5. Top 10 Strike Rates (min 500 legal balls faced)
```sql
SELECT
    batter,
    SUM(batsman_runs) AS runs,
    COUNT(*) AS balls_faced,
    ROUND(100.0 * SUM(batsman_runs) / COUNT(*), 2) AS strike_rate
FROM deliveries
WHERE extras_type IS NULL OR extras_type != 'wides'
GROUP BY batter
HAVING balls_faced >= 500
ORDER BY strike_rate DESC
LIMIT 10;
```

---

### Q6. Top 10 Wicket Takers
```sql
SELECT bowler, COUNT(*) AS wickets
FROM deliveries
WHERE is_wicket = 1
  AND dismissal_kind NOT IN ('run out', 'retired hurt', 'obstructing the field')
GROUP BY bowler
ORDER BY wickets DESC
LIMIT 10;
```

---

### Q7. Best Economy Rates (min 300 balls bowled)
```sql
SELECT
    bowler,
    COUNT(*) AS balls_bowled,
    SUM(total_runs) AS runs_conceded,
    ROUND(SUM(total_runs) * 6.0 / COUNT(*), 2) AS economy
FROM deliveries
GROUP BY bowler
HAVING balls_bowled >= 300
ORDER BY economy ASC
LIMIT 10;
```

---

### Q8. Dismissal Type Distribution
```sql
SELECT dismissal_kind, COUNT(*) AS count
FROM deliveries
WHERE is_wicket = 1
GROUP BY dismissal_kind
ORDER BY count DESC;
```

---

### Q9. Average First-Innings Score per Season
```sql
SELECT
    m.season AS season,
    ROUND(AVG(innings_total.total), 2) AS avg_first_innings_score
FROM (
    SELECT match_id, SUM(total_runs) AS total
    FROM deliveries
    WHERE inning = 1
    GROUP BY match_id
) AS innings_total
JOIN matches m ON innings_total.match_id = m.id
GROUP BY m.season
ORDER BY m.season;
```

---

### Q10. Top 10 Batting-Friendly Venues (Avg 1st Innings Score)
```sql
SELECT
    m.venue,
    ROUND(AVG(inning_score.score), 2) AS avg_score
FROM (
    SELECT match_id, SUM(total_runs) AS score
    FROM deliveries
    WHERE inning = 1
    GROUP BY match_id
) AS inning_score
JOIN matches m ON inning_score.match_id = m.id
GROUP BY m.venue
ORDER BY avg_score DESC
LIMIT 10;
```

---

### Q11. Runs Per Over Phase (Powerplay / Middle / Death)
```sql
SELECT
    CASE
        WHEN over BETWEEN 0 AND 5  THEN 'Powerplay (1-6)'
        WHEN over BETWEEN 6 AND 14 THEN 'Middle (7-15)'
        ELSE 'Death (16-20)'
    END AS phase,
    SUM(total_runs) AS total_runs,
    ROUND(AVG(total_runs), 3) AS avg_runs_per_ball
FROM deliveries
GROUP BY phase
ORDER BY total_runs DESC;
```

---

### Q12. Most Player of the Match Awards
```sql
SELECT player_of_match AS player, COUNT(*) AS awards
FROM matches
WHERE player_of_match IS NOT NULL
GROUP BY player_of_match
ORDER BY awards DESC
LIMIT 15;
```

---

### Q13. Bat First vs. Bat Second Win Rate
```sql
SELECT
    CASE
        WHEN (toss_decision = 'bat' AND toss_winner = winner)
          OR (toss_decision = 'field' AND toss_winner != winner)
        THEN 'Bat First Won'
        ELSE 'Bat Second Won'
    END AS batting_order_result,
    COUNT(*) AS matches
FROM matches
WHERE winner IS NOT NULL
GROUP BY batting_order_result;
```

---

### Q14. Most Extras (Wides + No-Balls) Conceded per Bowler
```sql
SELECT
    bowler,
    SUM(CASE WHEN extras_type = 'wides'   THEN 1 ELSE 0 END) AS wides,
    SUM(CASE WHEN extras_type = 'noballs' THEN 1 ELSE 0 END) AS noballs,
    SUM(CASE WHEN extras_type IN ('wides','noballs') THEN 1 ELSE 0 END) AS total_extras
FROM deliveries
GROUP BY bowler
ORDER BY total_extras DESC
LIMIT 10;
```

---

### Q15. Season-wise Performance of a Specific Team (e.g., Mumbai Indians)
```sql
SELECT
    m.season,
    COUNT(*) AS matches_played,
    SUM(CASE WHEN m.winner = 'Mumbai Indians' THEN 1 ELSE 0 END) AS wins,
    ROUND(100.0 * SUM(CASE WHEN m.winner = 'Mumbai Indians' THEN 1 ELSE 0 END) / COUNT(*), 1) AS win_pct
FROM matches m
WHERE m.team1 = 'Mumbai Indians' OR m.team2 = 'Mumbai Indians'
GROUP BY m.season
ORDER BY m.season;