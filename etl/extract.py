import os
from datetime import date
import pandas as pd
from pybaseball import batting_stats_bref, bwar_bat

RAW_DATA_DIR = "data/raw"

historical_seasons = range(2021, 2026)
current_season = 2026

def extract_batting_stats_historical(force_refresh=False):
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    cache_path = os.path.join(RAW_DATA_DIR, "batting_stats_bref_2021_2025.parquet")
    if os.path.exists(cache_path) and not force_refresh:
        return pd.read_parquet(cache_path)
    frames = []
    for season in historical_seasons:
        season_df = batting_stats_bref(season)
        season_df["season"] = season
        frames.append(season_df)
    combined = pd.concat(frames, ignore_index = True)
    combined.to_parquet(cache_path, index=False)
    return combined

def extract_batting_stats_current(force_refresh=False):
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    pull_date = date.today().isoformat()
    cache_path = os.path.join(RAW_DATA_DIR, f"batting_stats_bref_{current_season}_asof_{pull_date}.parquet")
    if os.path.exists(cache_path) and not force_refresh:
        return pd.read_parquet(cache_path)
    df = batting_stats_bref(current_season)
    df["season"] = current_season
    df.to_parquet(cache_path, index=False)
    return df

def extract_batting_stats(force_refresh_current=False):
    historical = extract_batting_stats_historical()
    current = extract_batting_stats_current(force_refresh=force_refresh_current)
    return pd.concat([historical, current], ignore_index=True)

def extract_batting_war(force_refresh=False):
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    pull_date = date.today().isoformat()
    cache_path = os.path.join(RAW_DATA_DIR, f"batting_war_asof_{pull_date}.parquet")
    if os.path.exists(cache_path) and not force_refresh:
        return pd.read_parquet(cache_path)
    df=bwar_bat(return_all=False)
    df.to_parquet(cache_path, index=False)
    return df

if __name__ == "__main__":
    df = extract_batting_stats()
    print(df.shape)
    print(df.head())