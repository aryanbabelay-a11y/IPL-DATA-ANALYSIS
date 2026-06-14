# 🏏 IPL Data Analysis Project (2007–2024)

> A full-stack data analysis project examining 17 seasons of the Indian Premier League across 1,095 matches and 260,920 ball-by-ball deliveries — uncovering team performance patterns, player dominance, toss strategy impact, and batting/bowling evolution.

---

## 📁 Project Structure

```
ipl-data-analysis/
│
├── data/
│   ├── matches.csv              # 1,095 match-level records (20 columns)
│   └── deliveries.csv           # 260,920 ball-by-ball delivery records (17 columns)
│
├── sql/
│   ├── postgresql_setup.sql     # CREATE TABLE + \copy + indexes + derived columns
│   └── ipl_queries.sql          # 15 analytical SQL queries
│
├── python/
│   └── ipl_eda.py               # Full EDA script (cleaning, charts, analysis)
│
├── powerbi/
│   └── IPL_Dashboard_Guide.md   # Power BI visual guide + DAX measures
│
├── report/
│   └── IPL_Analysis_Report.docx # Full written analysis report
│
└── README.md
```

---

## 📊 Dataset Overview

| File | Rows | Columns | Description |
|---|---|---|---|
| `matches.csv` | 1,095 | 20 | One row per IPL match — teams, toss, result, venue, date |
| `deliveries.csv` | 260,920 | 17 | One row per delivery — batter, bowler, runs, wicket info |

### matches.csv — Key Columns

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Unique match identifier (Primary Key) |
| `season` | VARCHAR | IPL season (e.g. `2008`, `2007/08`) |
| `date` | DATE | Match date |
| `team1`, `team2` | VARCHAR | Competing franchises |
| `toss_winner` | VARCHAR | Franchise that won the toss |
| `toss_decision` | VARCHAR | Decision: `bat` or `field` |
| `winner` | VARCHAR | Winning franchise (NULL = no result) |
| `result` | VARCHAR | Result type: `runs`, `wickets`, `tie`, `no result` |
| `result_margin` | INTEGER | Margin of victory in runs or wickets |
| `player_of_match` | VARCHAR | Best performer award winner |
| `venue`, `city` | VARCHAR | Match location |
| `umpire1`, `umpire2` | VARCHAR | On-field umpires |

### deliveries.csv — Key Columns

| Column | Type | Description |
|---|---|---|
| `match_id` | INTEGER | FK → matches.id |
| `inning` | SMALLINT | 1 = first innings, 2 = second |
| `batting_team` | VARCHAR | Team currently batting |
| `bowling_team` | VARCHAR | Team currently bowling |
| `over` | SMALLINT | Over number (0-indexed) |
| `ball` | SMALLINT | Ball number within the over |
| `batter`, `bowler` | VARCHAR | Players involved in the delivery |
| `batsman_runs` | SMALLINT | Runs scored by the batter |
| `extra_runs`, `total_runs` | SMALLINT | Extras and total on the delivery |
| `extras_type` | VARCHAR | Type: `wides`, `noballs`, `byes`, `legbyes` |
| `is_wicket` | SMALLINT | 1 if wicket fell, 0 otherwise |
| `dismissal_kind` | VARCHAR | Mode: caught, bowled, LBW, run out, etc. |
| `player_dismissed` | VARCHAR | Name of dismissed player (NULL if no wicket) |
| `fielder` | VARCHAR | Fielder involved in dismissal (if any) |

---

## 🎯 Problem Statement

> **"Analysing 17 Seasons of IPL (2007–2024): Team Performance, Player Dominance, Toss Impact, and Batting/Bowling Trends to Identify Winning Patterns and Key Success Factors in the Indian Premier League."**

---

## ❓ Research Questions

### Team Performance
1. Which teams have won the most matches across all seasons?
2. What is each team's win percentage (min. 30 matches)?
3. Does winning the toss significantly increase the chance of winning the match?
4. Is batting first or chasing the better post-toss strategy?
5. What is the average winning margin per team?

### Batting Analysis
6. Who are the top 10 all-time run-scorers?
7. Which batters have the highest strike rates (min. 500 balls faced)?
8. Which venues produce the highest average first-innings scores?
9. How has average first-innings score changed season over season?
10. Which over phase (powerplay / middle / death) contributes the most runs?

### Bowling Analysis
11. Who are the top 10 all-time wicket-takers?
12. Which bowlers have the best economy rates (min. 300 balls bowled)?
13. What is the most common dismissal type?
14. Which over is the most wicket-taking on average?
15. Which bowlers concede the most extras?

### Match Outcomes
16. What percentage of matches are won by teams batting first vs. second?
17. Which player has won the most Player of the Match awards?
18. Does the venue or city influence match outcomes?
19. How have scoring trends evolved across 17 seasons?
20. Which seasons had the most competitive results (smallest margins)?

---

## 🗄️ Database Setup (PostgreSQL)

### Prerequisites
- PostgreSQL 13+
- psql command-line OR pgAdmin / DBeaver

### Step 1 — Run setup script
```bash
psql -U your_username -d your_database -f sql/postgresql_setup.sql
```

### Step 2 — Update file paths
Edit the `\copy` commands in `postgresql_setup.sql`:
```sql
-- Change this to your actual CSV file path:
FROM '/absolute/path/to/matches.csv'
FROM '/absolute/path/to/deliveries.csv'
```

### Step 3 — Verify load
```sql
SELECT 'matches'    AS tbl, COUNT(*) FROM matches
UNION ALL
SELECT 'deliveries', COUNT(*) FROM deliveries;
-- Expected: matches = 1,095 | deliveries = 260,920
```

### Alternative — Python loading (if \copy gives issues)
```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://username:password@localhost:5432/your_db")

m = pd.read_csv("matches.csv")
m['date'] = pd.to_datetime(m['date'])
m.to_sql('matches', engine, if_exists='replace', index=False)

d = pd.read_csv("deliveries.csv")
d.to_sql('deliveries', engine, if_exists='replace', index=False, chunksize=5000)
```

---

## 🐍 Python EDA

### Requirements
```bash
pip install pandas numpy matplotlib seaborn
```

### Run
```bash
python python/ipl_eda.py
```

### Charts Generated
| File | Description |
|---|---|
| `matches_per_season.png` | Matches played per IPL season |
| `top_teams_wins.png` | Top 10 teams by total wins |
| `toss_impact.png` | Win % after toss by decision type |
| `team_win_pct.png` | Team win % (min. 30 matches) |
| `top_batters.png` | Top 10 all-time run-scorers |
| `runs_by_phase.png` | Total runs by powerplay / middle / death |
| `avg_runs_per_over.png` | Average runs scored per over (0–19) |
| `top_bowlers.png` | Top 10 all-time wicket-takers |
| `dismissal_types.png` | Dismissal type distribution |
| `avg_score_trend.png` | Average first-innings score by season |
| `potm.png` | Top 15 Player of the Match award winners |
| `venue_avg_score.png` | Top 10 batting-friendly venues |

---

## 📊 Power BI Dashboard — 5 Pages

| Page | Focus | Key Visuals |
|---|---|---|
| **1 — Overview** | Tournament KPIs | Cards, bar chart (wins), line (matches/season), donut (result type) |
| **2 — Teams** | Franchise performance | Clustered bar (win %), 100% stacked (toss impact), map (cities) |
| **3 — Batting** | Batter statistics | Bar (top scorers), scatter (runs vs. balls), line (over-wise rate) |
| **4 — Bowling** | Bowler statistics | Bar (top wickets), donut (dismissal type), scatter (economy vs. wickets) |
| **5 — Trends** | Season-over-season | Line (avg score trend), ribbon (team dominance), table (champions) |

### Key DAX Measures
```dax
Win % =
DIVIDE(
    CALCULATE(COUNTROWS(matches), matches[toss_won_match] = 1),
    COUNTROWS(matches), 0) * 100

Avg First Innings Score =
CALCULATE(
    AVERAGEX(VALUES(deliveries[match_id]), CALCULATE(SUM(deliveries[total_runs]))),
    deliveries[inning] = 1)

Strike Rate =
DIVIDE(SUM(deliveries[batsman_runs]), COUNTROWS(deliveries), 0) * 100

Economy Rate =
DIVIDE(SUM(deliveries[total_runs]), COUNTROWS(deliveries), 0) * 6
```

---

## 📈 Key Findings

| Metric | Value |
|---|---|
| Most wins — all time | **Mumbai Indians (144 wins)** |
| 2nd most wins | Chennai Super Kings (138 wins) |
| Toss-to-win conversion | 50.8% — barely above random |
| Best post-toss strategy | Field first → 53.9% win rate |
| All-time leading run scorer | **V Kohli — 8,014 runs** |
| All-time leading wicket taker | **YS Chahal — 205 wickets** |
| Average first-innings score | 165.5 runs (rising trend) |
| Most common dismissal | Caught (~55% of all wickets) |
| Most POTM awards | AB de Villiers (25 awards) |
| Bat first vs. chase win rate | 45.9% vs. **54.1%** |
| Highest run-rate phase | Death overs (~9.8 runs/over) |

---

## 🔧 Data Quality Notes

- `winner` has 5 NULL values (no-result matches) — excluded from win-rate analysis
- `result_margin` has 19 NULLs (ties/no result) — excluded from margin analysis only
- `method` is NULL for 1,074 matches — expected (NULL = normal result, not D/L)
- `player_dismissed` is NULL for ~240,000 deliveries — expected (no wicket on those balls)
- Season labels mixed: `2007/08` format in early seasons — normalised to end-year in Python

---

## 🛠️ Tools Used

| Tool | Purpose |
|---|---|
| Python (pandas, matplotlib, seaborn) | Data cleaning, EDA, visualisation |
| PostgreSQL | Relational database storage and SQL analysis |
| Power BI Desktop | Interactive dashboard |
| SQLAlchemy | Python → PostgreSQL data loading |

---

## 📋 Deliverables

- [x] `matches.csv` + `deliveries.csv` — Raw data
- [x] `postgresql_setup.sql` — Table creation + data loading
- [x] `ipl_queries.sql` — 15 analytical SQL queries
- [x] `ipl_eda.py` — Full Python EDA script
- [x] `IPL_Analysis_Report.docx` — Full written report
- [x] `IPL_Dashboard_Guide.md` — Power BI visual guide + DAX

---

*Seasons: 2007/08 to 2024 | Matches: 1,095 | Deliveries: 260,920 | Teams: 19 unique franchises*
