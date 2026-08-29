-- Player/award level: WAR leaderboard by season, league-wide
-- Business question: who were the most valuable players in each season by total
-- Wins Above Replacement (batting + pitching combined)? This is the data-driven
-- shortlist for MVP / Cy Young discussion, independent of actual award voting.
-- Two-way players have their batting and pitching WAR summed into a single total.


with batting_war as (
    select player_id, season, war
    from batting_stats
    where war is not null
),
pitching_war as (
    select player_id, season, war
    from pitching_stats
    where war is not null
),
combined_war as (
    select
        coalesce(b.player_id, p.player_id) as player_id,
        coalesce(b.season, p.season) as season,
        coalesce(b.war, 0) as batting_war,
        coalesce(p.war, 0) as pitching_war,
        coalesce(b.war, 0) + coalesce(p.war, 0) as total_war
    from batting_war b
    full outer join pitching_war p
    on b.player_id = p.player_id and b.season = p.season
),
ranked as (
    select
        player_id,
        season,
        batting_war,
        pitching_war,
        total_war,
        rank() over (partition by season order by total_war desc) as war_rank
    from combined_war
)
select
    pl.full_name,
    r.season,
    r.batting_war,
    r.pitching_war,
    r.total_war,
    r.war_rank
from ranked r
join players pl on r.player_id = pl.player_id
where r.war_rank <= 10
order by r.season, r.war_rank, pl.full_name;