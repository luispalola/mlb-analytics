-- View: qualified pitcher-season summary for the Tableau "ERA vs FIP" page.
-- One row per pitcher per season with innings_pitched >= 50 (starters + relievers).
-- Combines the ERA-vs-FIP gap (pitcher_era_fip_gap.sql) with the strikeout-to-walk
-- ratio (pitcher_kbb_ratio.sql).
-- is_qualified_starter flags the games_started >= 5 subset the ERA/FIP chart
-- focuses on; the K/BB view uses the full qualified pool.
-- No ORDER BY or ranking here -- Tableau handles that.


create or replace view vw_pitcher_era_fip as
with qualified as (
    select
        ps.player_id,
        ps.team_id,
        ps.season,
        ps.wins,
        ps.losses,
        ps.games,
        ps.games_started,
        ps.innings_pitched,
        ps.strikeouts,
        ps.walks,
        ps.era,
        ps.fip,
        ps.whip,
        ps.war
    from pitching_stats ps
    where ps.innings_pitched >= 50
)
select
    p.full_name,
    t.team_abbr,
    t.team_name,
    q.season,
    q.wins,
    q.losses,
    q.games,
    q.games_started,
    q.innings_pitched,
    q.era,
    q.fip,
    round(q.era-q.fip,2) as era_fip_gap,
    q.whip,
    q.strikeouts,
    q.walks,
    round(q.strikeouts::numeric / nullif(q.walks,0),2) as kbb_ratio,
    q.war,
    (coalesce(q.games_started, 0) >= 5) as is_qualified_starter
from qualified q
join players p on q.player_id = p.player_id
left join teams t on q.team_id = t.team_id;