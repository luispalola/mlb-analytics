-- Hitter level: wOBA vs. xwOBA gap among qualified hitters
-- Business question: which hitters' actual production differs most from what
-- their quality of contact (exit velocity, launch angle) predicts?
-- A hitter with wOBA well above xwOBA has been getting more than their batted
-- balls deserve (fortunate placement, seeing-eye singles) and is a candidate
-- for negative regression; the reverse suggests they've been unlucky and their
-- underlying contact quality says better results should be coming.
-- "Qualified" uses the same plate_appearances >= 300 threshold as
-- hitter_ops_percentile.sql.


with qualified_hitters as (
    select
        bs.player_id,
        p.full_name,
        bs.season,
        bs.plate_appearances,
        bs.woba,
        bs.est_woba
    from batting_stats bs
    join players p on bs.player_id = p.player_id
    where bs.plate_appearances >= 300
        and bs.woba is not null
        and bs.est_woba is not null
)
select
    full_name,
    season,
    plate_appearances,
    woba,
    est_woba,
    round(woba - est_woba, 3) as woba_gap,
    rank() over (order by (woba - est_woba) desc) as luckiest_rank
from qualified_hitters
order by woba_gap desc;