# ============================================================
# IPL DATA ANALYSIS — FULL EDA
# ============================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ── Plot styling ─────────────────────────────────────────────
sns.set_theme(style="darkgrid")
plt.rcParams.update({'figure.dpi': 120, 'figure.figsize': (12, 6)})
PALETTE = "Set2"

# ============================================================
# 1. LOAD DATA
# ============================================================
matches    = pd.read_csv("D:/matches.csv")
deliveries = pd.read_csv("D:/deliveries.csv")

print("Matches shape   :", matches.shape)
print("Deliveries shape:", deliveries.shape)
print("\nMatches columns :", list(matches.columns))
print("Deliveries cols :", list(deliveries.columns))

# ============================================================
# 2. DATA CLEANING
# ============================================================
# Fix date column
matches['date'] = pd.to_datetime(matches['date'])

# Standardise season labels (convert e.g. '2007/08' → 2008)
def clean_season(s):
    s = str(s)
    if '/' in s:
        return int(s.split('/')[0]) + 1
    return int(s)

matches['season_year'] = matches['season'].apply(clean_season)

# Toss win == match win flag
matches['toss_won_match'] = (matches['toss_winner'] == matches['winner']).astype(int)

# Drop rows where winner is NaN (no result matches)
matches_valid = matches.dropna(subset=['winner']).copy()

print("\nNull counts — matches:")
print(matches.isnull().sum())
print("\nNull counts — deliveries:")
print(deliveries.isnull().sum())

from sqlalchemy import create_engine
engine = create_engine('postgresql://postgres:aryan@localhost:5432/postgres')
# Store DataFrame to SQL table
matches.to_sql(
    name='matches',        # Table name
    con=engine,             # Database connection
    if_exists='replace',    # Options: 'fail', 'replace', 'append'
    index=False             # Don't write DataFrame index as a column
)

from sqlalchemy import create_engine
engine = create_engine('postgresql://postgres:aryan@localhost:5432/postgres')
# Store DataFrame to SQL table
deliveries.to_sql(
    name='deliveries',        # Table name
    con=engine,             # Database connection
    if_exists='replace',    # Options: 'fail', 'replace', 'append'
    index=False             # Don't write DataFrame index as a column
)

# ============================================================
# 3. UNIVARIATE ANALYSIS
# ============================================================

# -- 3a. Matches per season -----------------------------------
season_counts = matches.groupby('season_year')['id'].count().reset_index()
season_counts.columns = ['season_year', 'matches']
plt.figure(); sns.barplot(data=season_counts, x='season_year', y='matches', palette=PALETTE)
plt.title('Number of Matches per Season'); plt.xlabel('Season'); plt.ylabel('Matches')
plt.xticks(rotation=45); plt.tight_layout(); plt.savefig('matches_per_season.png'); plt.close()

# -- 3b. Win type distribution --------------------------------
plt.figure(figsize=(7, 5))
matches_valid['result'].value_counts().plot.pie(autopct='%1.1f%%', startangle=90, colors=sns.color_palette(PALETTE))
plt.title('Match Result Type Distribution'); plt.ylabel('')
plt.tight_layout(); plt.savefig('result_type_pie.png'); plt.close()

# -- 3c. Toss decision distribution --------------------------
plt.figure(figsize=(7, 5))
matches['toss_decision'].value_counts().plot.bar(color=sns.color_palette(PALETTE)[:2])
plt.title('Toss Decision — Bat vs Field'); plt.xlabel('Decision'); plt.ylabel('Count')
plt.tight_layout(); plt.savefig('toss_decision_bar.png'); plt.close()

# ============================================================
# 4. TEAM PERFORMANCE
# ============================================================

# -- 4a. Top 10 teams by wins ---------------------------------
top_winners = matches_valid['winner'].value_counts().head(10).reset_index()
top_winners.columns = ['team', 'wins']
plt.figure()
sns.barplot(data=top_winners, x='wins', y='team', palette='Blues_r')
plt.title('Top 10 Teams by Total Wins'); plt.xlabel('Wins'); plt.ylabel('Team')
plt.tight_layout(); plt.savefig('top_teams_wins.png'); plt.close()

# -- 4b. Toss win → match win analysis -----------------------
toss_impact = matches_valid.groupby('toss_decision')['toss_won_match'].mean().reset_index()
toss_impact.columns = ['Toss Decision', 'Win %']
toss_impact['Win %'] *= 100
print("\nToss Win → Match Win rate by decision:")
print(toss_impact)

plt.figure(figsize=(7, 5))
sns.barplot(data=toss_impact, x='Toss Decision', y='Win %', palette=PALETTE)
plt.title('Win % After Toss by Decision Type')
plt.axhline(50, ls='--', color='red', label='50% baseline')
plt.ylabel('Win % when toss is won'); plt.legend()
plt.tight_layout(); plt.savefig('toss_impact.png'); plt.close()

# -- 4c. Win % per team (min 30 matches) ---------------------
total_matches = pd.concat([matches_valid['team1'], matches_valid['team2']]).value_counts().reset_index()
total_matches.columns = ['team', 'played']
team_wins = matches_valid['winner'].value_counts().reset_index()
team_wins.columns = ['team', 'wins']
team_perf = total_matches.merge(team_wins, on='team')
team_perf['win_pct'] = (team_perf['wins'] / team_perf['played'] * 100).round(1)
team_perf = team_perf[team_perf['played'] >= 30].sort_values('win_pct', ascending=False)
print("\nTeam Win Percentages:")
print(team_perf[['team', 'played', 'wins', 'win_pct']])

plt.figure()
sns.barplot(data=team_perf, x='win_pct', y='team', palette='RdYlGn')
plt.title('Team Win % (min 30 matches)'); plt.xlabel('Win %'); plt.ylabel('Team')
plt.axvline(50, ls='--', color='red'); plt.tight_layout()
plt.savefig('team_win_pct.png'); plt.close()

# ============================================================
# 5. BATTING ANALYSIS
# ============================================================

# -- 5a. Top 10 run scorers -----------------------------------
top_batters = deliveries.groupby('batter')['batsman_runs'].sum().reset_index()
top_batters.columns = ['batter', 'total_runs']
top_batters = top_batters.sort_values('total_runs', ascending=False).head(10)
print("\nTop 10 Run Scorers:"); print(top_batters)

plt.figure()
sns.barplot(data=top_batters, x='total_runs', y='batter', palette='YlOrRd_r')
plt.title('Top 10 IPL Run Scorers'); plt.xlabel('Total Runs'); plt.ylabel('Batter')
plt.tight_layout(); plt.savefig('top_batters.png'); plt.close()

# -- 5b. Strike rate (min 500 balls faced) -------------------
balls_faced = deliveries[deliveries['extras_type'] != 'wides'].groupby('batter').size().reset_index(name='balls_faced')
runs_scored = deliveries.groupby('batter')['batsman_runs'].sum().reset_index()
strike_rate_df = balls_faced.merge(runs_scored, on='batter')
strike_rate_df['strike_rate'] = (strike_rate_df['batsman_runs'] / strike_rate_df['balls_faced'] * 100).round(2)
strike_rate_df = strike_rate_df[strike_rate_df['balls_faced'] >= 500].sort_values('strike_rate', ascending=False).head(10)
print("\nTop 10 Strike Rates (min 500 balls):"); print(strike_rate_df)

# -- 5c. Runs per over (powerplay vs middle vs death) --------
deliveries['over_phase'] = pd.cut(deliveries['over'], bins=[-1, 5, 14, 19],
                                   labels=['Powerplay (1-6)', 'Middle (7-15)', 'Death (16-20)'])
phase_runs = deliveries.groupby('over_phase')['total_runs'].sum().reset_index()
plt.figure(figsize=(8, 5))
sns.barplot(data=phase_runs, x='over_phase', y='total_runs', palette=PALETTE)
plt.title('Total Runs by Match Phase'); plt.xlabel('Over Phase'); plt.ylabel('Total Runs')
plt.tight_layout(); plt.savefig('runs_by_phase.png'); plt.close()

# -- 5d. Average over-wise run rate --------------------------
over_avg = deliveries.groupby('over')['total_runs'].mean().reset_index()
plt.figure()
sns.lineplot(data=over_avg, x='over', y='total_runs', marker='o', color='tomato')
plt.title('Average Runs Scored per Over (Overs 0–19)')
plt.xlabel('Over (0-indexed)'); plt.ylabel('Avg Runs per Over')
plt.tight_layout(); plt.savefig('avg_runs_per_over.png'); plt.close()

# ============================================================
# 6. BOWLING ANALYSIS
# ============================================================

# -- 6a. Top 10 wicket takers --------------------------------
wickets = deliveries[deliveries['is_wicket'] == 1]
top_bowlers = wickets.groupby('bowler')['is_wicket'].count().reset_index()
top_bowlers.columns = ['bowler', 'wickets']
top_bowlers = top_bowlers.sort_values('wickets', ascending=False).head(10)
print("\nTop 10 Wicket Takers:"); print(top_bowlers)

plt.figure()
sns.barplot(data=top_bowlers, x='wickets', y='bowler', palette='Purples_r')
plt.title('Top 10 IPL Wicket Takers'); plt.xlabel('Wickets'); plt.ylabel('Bowler')
plt.tight_layout(); plt.savefig('top_bowlers.png'); plt.close()

# -- 6b. Dismissal type distribution -------------------------
dismissal_counts = deliveries['dismissal_kind'].value_counts().reset_index()
dismissal_counts.columns = ['dismissal_kind', 'count']
plt.figure(figsize=(10, 5))
sns.barplot(data=dismissal_counts, x='count', y='dismissal_kind', palette='Set1')
plt.title('Dismissal Types Distribution'); plt.xlabel('Count'); plt.ylabel('Dismissal Kind')
plt.tight_layout(); plt.savefig('dismissal_types.png'); plt.close()

# -- 6c. Economy rate (min 300 balls) ------------------------
balls_bowled = deliveries.groupby('bowler').size().reset_index(name='balls')
runs_given   = deliveries.groupby('bowler')['total_runs'].sum().reset_index()
economy_df   = balls_bowled.merge(runs_given, on='bowler')
economy_df['economy'] = (economy_df['total_runs'] / (economy_df['balls'] / 6)).round(2)
economy_df   = economy_df[economy_df['balls'] >= 300].sort_values('economy').head(10)
print("\nTop 10 Best Economy Rates (min 300 balls):"); print(economy_df)

# ============================================================
# 7. SEASON TREND ANALYSIS
# ============================================================

# -- 7a. Avg first-innings score per season ------------------
merged = deliveries.merge(matches[['id', 'season_year']], left_on='match_id', right_on='id')
first_innings = merged[merged['inning'] == 1]
avg_score_season = first_innings.groupby(['match_id', 'season_year'])['total_runs'].sum().reset_index()
avg_score_season = avg_score_season.groupby('season_year')['total_runs'].mean().reset_index()
avg_score_season.columns = ['season_year', 'avg_first_innings_score']
plt.figure()
sns.lineplot(data=avg_score_season, x='season_year', y='avg_first_innings_score', marker='o', color='steelblue')
plt.title('Average First-Innings Score per Season')
plt.xlabel('Season Year'); plt.ylabel('Average Score')
plt.tight_layout(); plt.savefig('avg_score_trend.png'); plt.close()

# ============================================================
# 8. PLAYER OF THE MATCH
# ============================================================
potm = matches['player_of_match'].value_counts().head(15).reset_index()
potm.columns = ['player', 'awards']
plt.figure()
sns.barplot(data=potm, x='awards', y='player', palette='coolwarm')
plt.title('Top 15 Player of the Match Award Winners')
plt.xlabel('Awards'); plt.ylabel('Player')
plt.tight_layout(); plt.savefig('potm.png'); plt.close()

# ============================================================
# 9. VENUE ANALYSIS
# ============================================================
venue_runs = merged[merged['inning'] == 1].groupby(['match_id'])['total_runs'].sum().reset_index()
venue_runs = venue_runs.merge(matches[['id', 'venue']], left_on='match_id', right_on='id')
venue_avg  = venue_runs.groupby('venue')['total_runs'].mean().sort_values(ascending=False).head(10).reset_index()
venue_avg.columns = ['venue', 'avg_score']
plt.figure()
sns.barplot(data=venue_avg, x='avg_score', y='venue', palette='magma')
plt.title('Top 10 High-Scoring Venues (Avg First-Innings Score)')
plt.xlabel('Avg Score'); plt.ylabel('Venue')
plt.tight_layout(); plt.savefig('venue_avg_score.png'); plt.close()

print("\n✅ All charts saved. EDA complete!")
```