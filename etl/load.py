import os
import sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import text
from config.db_config import engine

def load_players(df):
    with engine.begin() as conn:
        for row in df.itertuples(index=False):
            conn.execute(
                text("""
                    INSERT INTO players (mlbam_id, full_name)
                    VALUES (:mlbam_id, :full_name)
                    ON CONFLICT (mlbam_id) DO UPDATE
                    SET full_name = EXCLUDED.full_name
                """),
                {"mlbam_id": row.mlbam_id, "full_name": row.full_name}
            )


def get_team_lookup():
    return pd.read_sql("SELECT team_id, team_abbr FROM teams", engine)

def get_player_lookup():
    return pd.read_sql("SELECT player_id, mlbam_id FROM players", engine)

def prepare_batting_stats(df):
    teams = get_team_lookup()
    players = get_player_lookup()
    df = df.merge(players, left_on='mlbID', right_on='mlbam_id', how='left')
    df = df.merge(teams, on='team_abbr', how='left')
    df = df.rename(columns={
        'G': 'games_played',
        'PA': 'plate_appearances',
        'AB': 'at_bats',
        'H': 'hits',
        '2B': 'doubles',
        '3B': 'triples',
        'HR': 'home_runs',
        'RBI': 'rbi',
        'BB': 'walks',
        'SO': 'strikeouts',
        'SB': 'stolen_bases',
        'BA': 'avg',
        'OBP': 'obp',
        'SLG': 'slg',
        'OPS': 'ops',
        'WAR': 'war',
    })
    cols = ['player_id', 'team_id', 'season', 'games_played', 'plate_appearances', 'at_bats', 'hits',
            'doubles', 'triples', 'home_runs', 'rbi', 'walks', 'strikeouts', 'stolen_bases', 'avg', 'obp', 'slg', 'ops', 'war']
    return df[cols]


def load_batting_stats(df):
    df = df.astype(object).where(pd.notnull(df), None)
    with engine.begin() as conn:
        for row in df.itertuples(index=False):
            conn.execute(
                text("""
                    INSERT INTO batting_stats (
                        player_id, team_id, season, games_played, plate_appearances, at_bats,
                        hits, doubles, triples, home_runs, rbi, walks, strikeouts, stolen_bases,
                        avg, obp, slg, ops, war
                    )
                    VALUES (
                        :player_id, :team_id, :season, :games_played, :plate_appearances, :at_bats,
                        :hits, :doubles, :triples, :home_runs, :rbi,  :walks, :strikeouts, :stolen_bases,
                        :avg, :obp, :slg, :ops, :war
                    )
                    ON CONFLICT (player_id, season) DO UPDATE SET
                        team_id = EXCLUDED.team_id,
                        games_played = EXCLUDED.games_played,
                        plate_appearances = EXCLUDED.plate_appearances,
                        at_bats = EXCLUDED.at_bats,
                        hits = EXCLUDED.hits,
                        doubles = EXCLUDED.doubles,
                        triples = EXCLUDED.triples,
                        home_runs = EXCLUDED.home_runs,
                        rbi = EXCLUDED.rbi,
                        walks = EXCLUDED.walks,
                        strikeouts = EXCLUDED.strikeouts,
                        stolen_bases = EXCLUDED.stolen_bases,
                        avg = EXCLUDED.avg,
                        obp = EXCLUDED.obp,
                        slg = EXCLUDED.slg,
                        ops = EXCLUDED.ops,
                        war = EXCLUDED.war,
                        data_as_of = CURRENT_DATE
                """),
                row._asdict()
            )


def prepare_pitching_stats(df):
    teams = get_team_lookup()
    players = get_player_lookup()
    df = df.merge(players, left_on='mlbID', right_on='mlbam_id', how='left')
    df = df.merge(teams, on='team_abbr', how='left')
    df = df.rename(columns={
        'W':'wins',
        'L':'losses',
        'ERA':'era',
        'G':'games',
        'GS':'games_started',
        'IP':'innings_pitched',
        'SO':'strikeouts',
        'BB': 'walks',
        'WHIP':'whip',
        'FIP':'fip',
        'WAR':'war',
    })
    cols=['player_id', 'team_id', 'season', 'wins', 'losses', 'era', 'games', 'games_started',
          'innings_pitched', 'strikeouts', 'walks', 'whip', 'fip', 'war']
    return df[cols]


def load_pitching_stats(df):
    df = df.astype(object).where(pd.notnull(df), None)
    with engine.begin() as conn:
        for row in df.itertuples(index=False):
            conn.execute(
                text("""
                    INSERT INTO pitching_stats (
                        player_id, team_id, season, wins, losses, era, games, games_started,
                        innings_pitched, strikeouts, walks, whip, fip, war
                    )
                    VALUES (
                        :player_id, :team_id, :season, :wins, :losses, :era, :games, :games_started,
                        :innings_pitched, :strikeouts, :walks, :whip, :fip, :war
                    )
                    ON CONFLICT (player_id, season) DO UPDATE SET
                        team_id = EXCLUDED.team_id,
                        wins = EXCLUDED.wins,
                        losses = EXCLUDED.losses,
                        era = EXCLUDED.era,
                        games = EXCLUDED.games,
                        games_started = EXCLUDED.games_started,
                        innings_pitched = EXCLUDED.innings_pitched,
                        strikeouts = EXCLUDED.strikeouts,
                        walks = EXCLUDED.walks,
                        whip = EXCLUDED.whip,
                        fip = EXCLUDED.fip,
                        war = EXCLUDED.war,
                        data_as_of = CURRENT_DATE
                """),
                row._asdict()
            )



def prepare_games(df):
    teams=get_team_lookup()
    home_teams = teams.rename(columns={'team_id':'home_team_id', 'team_abbr':'home_team_abbr'})
    away_teams = teams.rename(columns={'team_id':'away_team_id', 'team_abbr':'away_team_abbr'})
    df=df.merge(home_teams, on='home_team_abbr', how='left')
    df=df.merge(away_teams, on='away_team_abbr', how='left')
    df=df.rename(columns={'game_num': 'game_number'})
    cols = ['game_date', 'season', 'home_team_id', 'away_team_id', 'home_score', 'away_score', 'game_number']
    return df[cols]

def load_games(df):
    df = df.astype(object).where(pd.notnull(df), None)
    with engine.begin() as conn:
        for row in df.itertuples(index=False):
            conn.execute(
                text("""
                    INSERT INTO games (
                        game_date, season, home_team_id, away_team_id, home_score, away_score, game_number
                    )
                    VALUES (
                        :game_date, :season, :home_team_id, :away_team_id, :home_score, :away_score, :game_number
                    )
                    ON CONFLICT (game_date, home_team_id, away_team_id, game_number) DO UPDATE SET
                        home_score = EXCLUDED.home_score,
                        away_score = EXCLUDED.away_score
                """),
                row._asdict()
            )



if __name__ == "__main__":
    from transform import build_players_dimension, build_batting_stats, build_pitching_stats, build_games
    players_df = build_players_dimension()
    load_players(players_df)
    print(f"Loaded {len(players_df)} players")
    batting_df = prepare_batting_stats(build_batting_stats())
    load_batting_stats(batting_df)
    print(f"Loaded {len(batting_df)} batting stats lines")
    pitching_df = prepare_pitching_stats(build_pitching_stats())
    load_pitching_stats(pitching_df)
    print(f"Loaded {len(pitching_df)} pitching stats lines")
    games_df = prepare_games(build_games())
    load_games(games_df)
    print(f"Loaded {len(games_df)} games")