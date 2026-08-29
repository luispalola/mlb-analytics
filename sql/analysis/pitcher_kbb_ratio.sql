-- Pitcher-level: Strikeout-to-walk ratio leaders among qualified pitchers
-- Business question: which pitchers show the strongest combination of missing bats
-- and avoiding walks? K/BB ratio is a secondary "true talent" signal alongside FIP,
-- since strikeouts and walks are almost entirely within a pitcher's own control
-- (unlike balls in play, which depend heavily on defense and luck).

with qualified_pitchers as(
    select
        ps.player_id,
        p.full_name,
        ps.season,
        ps.innings_pitched,
        ps.strikeouts,
        ps.walks
    from pitching_stats ps
    join players p on ps.player_id = p.player_id
    where ps.innings_pitched >= 50
        and ps.walks > 0
)
select
    full_name,
    season,
    innings_pitched,
    strikeouts,
    walks,
    round(strikeouts::numeric/walks,2) as kbb_ratio,
    rank() over (partition by season order by (strikeouts::numeric/walks) desc) as kbb_rank
from qualified_pitchers
order by season, kbb_rank;