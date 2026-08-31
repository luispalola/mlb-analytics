-- View: player-season award-contention summary for the Tableau "award case" page.
-- Spine: one row per player per season that recorded batting OR pitching WAR.
-- Merges three source queries:
--   - total WAR (batting + pitching) and its per-season rank  ... player_war_leaderboard.sql
--   - OPS percentile / quartile / rank among PA >= 300 hitters ... hitter_ops_percentile.sql
--   - year-over-year batting WAR & OPS change, consecutive PA >= 200 seasons ... hitter_yoy_improvement.sql
-- ops_* and *_change columns are NULL for player-seasons outside those
-- narrower populations (non-hitters, < 300 PA, non-consecutive seasons).
-- war_rank is kept for every row (unfiltered) so Tableau can slice top-N itself.




create or replace view vw_award_contenders as
with batting_side as (
    select player_id, team_id, season, war, plate_appearances, ops
    from batting_stats
),
pitching_side as (
    select player_id, team_id, season, war, innings_pitched, era, fip
    from pitching_stats
),
combined as (
    select
        coalesce(b.player_id, p.player_id) as player_id,
        coalesce(b.team_id, p.team_id) as team_id,
        coalesce(b.season, p.season) as season,
        coalesce(b.war,0) as batting_war,
        coalesce(p.war,0) as pitching_war,
        coalesce(b.war,0) + coalesce(p.war,0) as total_war,
        b.plate_appearances,
        b.ops,
        p.innings_pitched,
        p.era,
        p.fip
    from batting_side b
    full outer join pitching_side p
        on b.player_id = p.player_id and b.season=p.season
),
war_ranked as (
    select combined.*,
        rank() over (partition by season order by total_war desc) as war_rank
    from combined
),
ops_pctile as (
    select player_id, season,
        round((percent_rank() over (partition by season order by ops))::numeric, 3) as ops_percentile,
        ntile(4) over (partition by season order by ops) as ops_quartile,
        rank() over (partition by season order by ops desc) as ops_rank
    from batting_stats
    where plate_appearances >= 300 and ops is not null
),
hitter_seasons as (
    select player_id, season, war, ops
    from batting_stats
    where plate_appearances >= 200 and war is not null and ops is not null
),
yoy as (
    select player_id, season,
        war as current_war,
        ops as current_ops,
        lag(season) over w as prior_season,
        lag(war) over w as prior_war,
        lag(ops) over w as prior_ops
    from hitter_seasons
    window w as (partition by player_id order by season)
)
select
    pl.full_name,
    t.team_abbr,
    t.team_name,
    wr.season,
    wr.batting_war,
    wr.pitching_war,
    wr.total_war,
    wr.war_rank,
    wr.plate_appearances,
    wr.ops,
    op.ops_percentile,
    op.ops_quartile,
    op.ops_rank,
    wr.innings_pitched,
    wr.era,
    wr.fip,
    y.prior_season,
    y.prior_war,
    case when y.prior_season = wr.season - 1
        then round(y.current_war - y.prior_war, 1) end as war_change,
    y.prior_ops,
    case when y.prior_season = wr.season - 1
        then round(y.current_ops-y.prior_ops,3) end as ops_change,
    (wr.plate_appearances >= 300) as is_qualified_hitter
from war_ranked wr
join players pl on wr.player_id = pl.player_id
left join teams t on wr.team_id = t.team_id
left join ops_pctile op on op.player_id = wr.player_id and op.season = wr.season
left join yoy y on y.player_id = wr.player_id and y.season = wr.season;