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

if __name__ == "__main__":
    from transform import build_players_dimension
    df = build_players_dimension()
    load_players(df)
    print(f"Loaded {len(df)} players")