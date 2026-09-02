-- one row per team per game; each game makes two rows, one for each team (~28,318 rows across 6 seasons)
-- feeds the line chart on the tableau "team over/underperformers" page that shows how a team's form rises and falls over a season.
-- same core logic as rolling_win_percentage.sql, plus a few columns tableau
-- needs a game number within the season (1,2,3,...), a running season long win %, and the opponent and home/away flag for hover tooltips.
-- no order by on purpose as tableau does its own sorting


create or replace view vw_team_rolling_winpct as
with team_game_log as (
    select
        home_team_id as team_id,
        away_team_id as opponent_id,
        season, game_date, game_number,
        'home' as home_away,
        home_score as runs_for,
        away_score as runs_against,
        case when home_score > away_score then 1 else 0 end as win
    from games
    union all
    select
        away_team_id,
        home_team_id,
        season, game_date, game_number,
        'away',
        away_score,
        home_score,
        case when away_score > home_score then 1 else 0 end
    from games
)
select
    t.team_name,
    t.team_abbr,
    t.league,
    t.division,
    gl.season,
    gl.game_date,
    gl.game_number,
    row_number() over w as game_seq,
    gl.home_away,
    opp.team_abbr as opponent_abbr,
    gl.runs_for,
    gl.runs_against,
    gl.win,
    sum(gl.win) over (w rows between unbounded preceding and current row) as wins_to_date,
    count(*) over (w rows between unbounded preceding and current row) as games_to_date,
    round(avg(gl.win) over (w rows between unbounded preceding and current row), 3) as season_win_pct_to_date,
    round(avg(gl.win) over (w rows between 9 preceding and current row), 3) as rolling_10_game_win_pct
from team_game_log gl
join teams t on gl.team_id = t.team_id
left join teams opp on gl.opponent_id = opp.team_id
window w as (
    partition by gl.team_id, gl.season
    order by gl.game_date, gl.game_number
);
    