-- View: team-season performance summary for the Tableau "team over/underperformers" page.
-- One row per team per season (180 rows: 30 teams x 6 seasons).
-- Combines actual vs. Pythagorean expected wins (team_performance.sql) with
-- season-over-season run differential change (run_differential_swing.sql).
-- No ORDER BY or ranking here -- Tableau handles sorting/ranking on its side.


create or replace view vw_team_performance as
with team_game_results as (
    select home_team_id as team_id, season,
        home_score as runs_scored, away_score as runs_allowed,
        case when home_score > away_score then 1 else 0 end as win
    from games
    union all
    select away_team_id as team_id, season,
        away_score as runs_scored, home_score as runs_allowed,
        case when away_score > home_score then 1 else 0 end as win
    from games
),
team_season_totals as (
    select team_id, season,
        count(*) as games_played,
        sum(win) as actual_wins,
        sum(runs_scored) as runs_scored,
        sum(runs_allowed) as runs_allowed
    from team_game_results
    group by team_id, season
),
team_season as (
    select team_id, season, games_played, actual_wins,
        games_played-actual_wins as actual_losses,
        runs_scored, runs_allowed,
        runs_scored-runs_allowed as run_differential,
        round(
            (power(runs_scored::numeric, 2)
            / (power(runs_scored::numeric, 2) + power(runs_allowed::numeric, 2)))
            * games_played, 1
        ) as expected_wins
    from team_season_totals
),
with_prior as (
    select team_id, season, games_played, actual_wins, actual_losses,
        runs_scored, runs_allowed, run_differential, expected_wins,
        lag(run_differential) over (partition by team_id order by season) as prior_run_differential
    from team_season
)
select
    t.team_name,
    t.team_abbr,
    t.league,
    t.division,
    w.season,
    w.games_played,
    w.actual_wins,
    w.actual_losses,
    w.runs_scored,
    w.runs_allowed,
    w.run_differential,
    w.expected_wins,
    round(w.actual_wins-w.expected_wins, 1) as win_gap,
    w.prior_run_differential,
    w.run_differential-w.prior_run_differential as run_diff_change
from with_prior w
join teams t on w.team_id = t.team_id;