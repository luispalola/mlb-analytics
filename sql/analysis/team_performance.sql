-- team level: actual wins vs. pythagorean expected wins
-- question: which teams are winning more (or fewer) games than their run
-- differential predicts? a team significantly outperforming its pythagorean expectation
-- is a candidate for regression and is overachieving in ways that may not be sustainable


WITH team_game_results AS (
    select home_team_id as team_id, season, home_score as runs_scored, away_score as runs_allowed,
        case when home_score > away_score then 1 else 0 end as win
    from games
    union all
    select away_team_id as team_id, season, away_score as runs_scored, home_score as runs_allowed,
        case when away_score > home_score then 1 else 0 end as win
    from games
),
team_season_totals as (
    select team_id, season, count(*) as games_played, sum(win) as actual_wins,
        sum(runs_scored) as runs_scored, sum(runs_allowed) as runs_allowed
    from team_game_results
    group by team_id, season
),
pythagorean as (
    select team_id, season, games_played, actual_wins, runs_scored, runs_allowed,
        round(
            (power(runs_scored::numeric, 2) / (power(runs_scored::numeric, 2) + power(runs_allowed::numeric, 2)))
            * games_played, 1
        ) as expected_wins
    from team_season_totals
)
select
    t.team_name,
    p.season,
    p.games_played,
    p.actual_wins,
    p.expected_wins,
    round(p.actual_wins - p.expected_wins, 1) as win_gap
from pythagorean p
join teams t on p.team_id = t.team_id
order by win_gap desc;