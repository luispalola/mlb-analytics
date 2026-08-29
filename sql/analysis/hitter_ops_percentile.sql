-- Player/award level: OPS percentile rank among qualified hitters, by season
-- Business question: where does each hitter's OPS fall relative to the rest of
-- the league that season? Percentile rank normalizes across seasons with
-- different run environments, so a .900 OPS in a low-offense year gets credited
-- appropriately rather than judged against a fixed number.
-- "Qualified" here is plate_appearances >= 300 -- below MLB's official 502
-- (3.1 PA per team game), chosen so the in-progress 2026 season still returns a
-- usable pool of hitters.


with qualified_hitters as (
    select
        bs.player_id,
        p.full_name,
        bs.season,
        bs.plate_appearances,
        bs.ops
    from batting_stats bs
    join players p on bs.player_id = p.player_id
    where bs.plate_appearances >= 300
        and bs.ops is not null
)
select
    full_name,
    season,
    plate_appearances,
    ops,
    round((percent_rank() over (partition by season order by ops))::numeric, 3) as ops_percentile,
    ntile(4) over (partition by season order by ops) as ops_quartile,
    rank() over (partition by season order by ops desc) as ops_rank
from qualified_hitters
order by season, ops_rank, full_name;