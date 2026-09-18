# MLB Analytics Dashboard

Which teams, pitchers, and hitters are over/underperforming what their underlying stats predict? And how does that connect to who actually deserves recognition for major awards?

**Live Dashboard:** https://public.tableau.com/app/profile/luis.palola/viz/MLBAnalyticsDashboard/Pitching

**Repo:** https://github.com/luispalola/mlb-analytics

---

## Core Problem

Regular season baseball is long and full of noise. A team can win more games than its run differential suggests it should. A pitcher's ERA can diverge sharply from what his strikeouts, walks, and home runs allowed predict. A hitter can outproduce (or underproduce) what the actual quality of his contact says he should.

This project applies the same "actual vs expected" lens at three different levels (team, pitcher, and hitter) across six MLB seasons (2021-2026, with 2026 as a live, in-progress season), and turns the results into an interactive Tableau dashboard.

One thing this project doesn't try to do: predict playoff outcomes. Regular season underlying stats are a reasonable signal for team quality, but a playoff series played across just a few games is dominated by small sample variance.

## Key Findings

Real results the dashboard presents (cross checked against actual outcomes):

- **2024 Colorado Rockies** - a 61-101 season correctly flagged as one of the largest gaps between actual and Pythagorean-expected wins (a formula that estimates expected wins from runs scored and allowed) in the dataset.
- **2021 Seattle Mariners** - one of the clearest examples of a team overachieving its run differential.
- **Cy Young races** - an award given to a league's best pitcher, the Pitching WAR leaderboard independently shows the real Cy Young winners each year (Tarik Skubal in 2024; Paul Skenes and Tarik Skubal in 2025) without being told the actual result in advance.

## Tech Stack

- **Python** (pandas, numpy, `pybaseball`, SQLAlchemy) runs the whole pipeline.
- **PostgreSQL 16** holds the data, with the analysis layer leaning on window functions, CTEs, and views.
- **Tableau Public** powers the dashboards — cross-filtering and highlight actions tie the team, pitcher, and hitter views together.
- Data comes from **Baseball-Reference** (via `pybaseball`) and **Baseball Savant/Statcast** for hitter expected stats.

## Architecture

```
Extract (pybaseball)  →  Transform (pandas)  →  Load (Postgres, upsert)
↓
SQL analysis views
↓
CSV export → Tableau Public
```

`etl/extract.py` pulls season batting/pitching stats, game-by-game results, WAR, and Statcast expected stats, caching each pull locally as parquet — date-stamped for the current season since it's still in progress, permanent for the completed historical ones.

From there, `etl/transform.py` cleans and merges everything: fixing accented-name encoding bugs, resolving team abbreviations across a mid-project franchise rename (Athletics → ATH), computing FIP by hand since Baseball-Reference doesn't provide it, and merging in the WAR and expected-stats pulls.

**Load** (`etl/load.py`) upserts the result into PostgreSQL, keyed on `(player_id, season)` and `(game_date, home_team, away_team, game_number)`.

The **SQL layer** (`sql/analysis/`, `sql/views/`) computes Pythagorean win expectancy, ERA–FIP gap, K/BB leaders, WAR leaderboards, and the wOBA-vs-xwOBA gap, each with its own qualification threshold (50+ IP for pitchers, for example) baked in as a boolean flag so Tableau filters the right population per chart.

Finally, those four views get exported to CSV and connected in **Tableau Public**, split across three dashboards: Team Performance, Pitching, and Hitters.


## Data Sources

All batting/pitching stats come from **Baseball-Reference**, via `pybaseball`'s `batting_stats_range()` / `pitching_stats_range()`. FanGraphs (the original planned source) is blocked by Cloudflare's anti-bot protection and was dropped early and WAR is instead pulled separately via `bwar_bat()` / `bwar_pitch()`. Hitter expected stats (wOBA/xwOBA) come from Baseball Savant via `statcast_batter_expected_stats()`.

## How to Run It

```
git clone https://github.com/luispalola/mlb-analytics
cd mlb-analytics
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your Postgres credentials
```

Set up the database:

```
psql -d your_db -f sql/schema/create_tables.sql
psql -d your_db -f sql/schema/seed_teams.sql
```

Run the pipeline:

```
python etl/extract.py
python etl/load.py
```

Then run the view definitions in `sql/views/` against your database, export each view to CSV, and connect them in Tableau or just open the [live dashboard](https://public.tableau.com/app/profile/luis.palola/viz/MLBAnalyticsDashboard/Pitching) directly.

## Known Limitations
- **2026 is a in-progress season.** Any stat for 2026 is a snapshot as of the last data refresh, not a final-season total so treat it as a moving target, not a completed record.
- **K/BB Leaders includes both starters and relievers.** A reliever's K/BB ratio can be inflated by a small sample of appearances. This isn't a starters only leaderboard.
- **The current season's data only refreshes when the pipeline is manually re-run.** There's no scheduled re run for the 2026 data set. During development, a caching bug caused the current season's game data to silently freeze at its first pull date and never update on later runs, despite the pipeline appearing to run successfully. This was found by cross checking a team's win total against Baseball-Reference's live page and fixed by date stamping the current season's cache files the same way every other extract function already did.
- **A few historical stat lines may not perfectly match Baseball-Reference's own season-totals page.** This happens because the stats are pulled by adding up daily game logs instead of reading Baseball-Reference's season-totals page directly. Only a few players were affected out of everyone checked, and the gap was small, so I didn't dig into every single player.

## Project Structure

```
mlb-analytics/
├── etl/                  # extract.py, transform.py, load.py
├── sql/
│   ├── schema/           # table definitions, team seed data
│   ├── analysis/         # one query per analysis question
│   └── views/            # Tableau-facing views
├── config/                # database connection config
└── tableau/data/          # CSV exports feeding the Tableau workbook
```