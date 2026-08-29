-- Team-level: Season-over-season change in run differential
-- Business question: which teams saw the biggest year-over-year swing in run
-- differential (for better or worse)? A sharp change suggests a team's underlying
-- quality shifted meaningfully, not just their win-loss record.

with team_run_diff as (
    select home_team_id as team_id, season, home_score as runs_scored, away_score as runs_allowed
    from games
    union all
    select away_team_id as team_id, season, away_score as runs_scored, home_score as runs_allowed
    from games
),
team_season_diff as (
    select team_id, season, sum(runs_scored) - sum(runs_allowed) as run_differential
    from team_run_diff
    group by team_id, season
),
with_prior_season as (
    select team_id, season, run_differential,
        lag(run_differential) over (partition by team_id order by season) as prior_run_differential
    from team_season_diff
)
select
    t.team_name,
    w.season,
    w.prior_run_differential,
    w.run_differential,
    (w.run_differential-w.prior_run_differential) as run_diff_change,
    rank() over (order by abs(w.run_differential-w.prior_run_differential) desc) as swing_rank
from with_prior_season w
join teams t on w.team_id = t.team_id
where w.prior_run_differential is not null
order by swing_rank;