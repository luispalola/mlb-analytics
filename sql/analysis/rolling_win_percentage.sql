-- Team-level: Rolling 10-game win percentage
-- Business question: is a team's recent form trending up or down, independent
-- of their full-season record? Useful for seeing whether a hot or cold streak
-- (and any related over/underperformance vs. Pythagorean expectation) is
-- continuing or correcting over time.

with team_game_log as (
    select home_team_id as team_id, season, game_date, game_number,
        case when home_score > away_score then 1 else 0 end as win
    from games
    union all
    select away_team_id as team_id, season, game_date, game_number,
        case when away_score > home_score then 1 else 0 end as win
    from games
)
select
    t.team_name,
    gl.season,
    gl.game_date,
    gl.game_number,
    gl.win,
    round(
        avg(gl.win) over (
            partition by gl.team_id, gl.season
            order by gl.game_date, gl.game_number
            rows between 9 preceding and current row
        ), 3
    ) as rolling_10_game_win_pct
from team_game_log gl
join teams t on gl.team_id = t.team_id
order by t.team_name, gl.season, gl.game_date, gl.game_number