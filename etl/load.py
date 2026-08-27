import os
import sys
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


if __name__ == "__main__":
    from transform import build_players_dimension
    df = build_players_dimension()
    load_players(df)
    print(f"Loaded {len(df)} players")