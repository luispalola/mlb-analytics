-- Pitcher-level: ERA vs. FIP gap among qualified starters
-- Business question: which starting pitchers' ERA differs most from their FIP?
-- A pitcher with ERA well above FIP may be getting unlucky (weak defense, bad
-- sequencing of hits) and is a candidate for positive regression; the reverse
-- suggests they've been fortunate and may regress the other way.

with qualified_starters as (
    select
        ps.player_id,
        p.full_name,
        ps.season,
        ps.era,
        ps.fip,
        ps.innings_pitched,
        ps.games_started
    from pitching_stats ps
    join players p on ps.player_id = p.player_id
    where ps.games_started >= 5
        and ps.innings_pitched >= 50
        and ps.era is not null
        and ps.fip is not null
)
select
    full_name,
    season,
    innings_pitched,
    era,
    fip,
    round(era-fip,2) as era_fip_gap,
    rank() over (order by (era-fip) desc) as unluckiest_rank
from qualified_starters
order by era_fip_gap desc;