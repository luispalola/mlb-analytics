-- Player/award level: largest year-over-year improvement in WAR and OPS
-- Business question: which hitters took the biggest step forward from one
-- season to the next? Large positive jumps are breakout candidates; sorting the
-- other way surfaces collapses. Restricted to consecutive seasons where the
-- player had a real workload in both (plate_appearances >= 200), so the delta
-- reflects a performance change rather than a sample-size artifact.


with hitter_seasons as (
    select
        bs.player_id,
        bs.season,
        bs.plate_appearances,
        bs.war,
        bs.ops
    from batting_stats bs
    where bs.plate_appearances >= 200
        and bs.war is not null
        and bs.ops is not null
),
with_prior as (
    select
        player_id,
        season,
        war,
        ops,
        lag(season) over w as prior_season,
        lag(war) over w as prior_war,
        lag(ops) over w as prior_ops
    from hitter_seasons
    window w as (partition by player_id order by season)
)
select
    p.full_name,
    wp.prior_season,
    wp.season,
    wp.prior_war,
    wp.war,
    round(wp.war-wp.prior_war, 1) as war_change,
    wp.prior_ops,
    wp.ops,
    round(wp.ops-wp.prior_ops,3) as ops_change,
    rank() over (order by (wp.war-wp.prior_war) desc) as war_gain_rank,
    rank() over (order by (wp.ops-wp.prior_ops) desc) as ops_gain_rank
from with_prior wp
join players p on wp.player_id = p.player_id
where wp.prior_season = wp.season - 1
order by war_gain_rank;