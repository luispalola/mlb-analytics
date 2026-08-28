import os
from datetime import date
import pandas as pd
import numpy as np
import pybaseball.team_results as _team_results
from pybaseball import batting_stats_bref, bwar_bat, pitching_stats_bref, bwar_pitch, schedule_and_record

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



def extract_pitching_stats_historical(force_refresh=False):
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    cache_path = os.path.join(RAW_DATA_DIR, "pitching_stats_bref_2021_2025.parquet")
    if os.path.exists(cache_path) and not force_refresh:
        return pd.read_parquet(cache_path)
    frames = []
    for season in historical_seasons:
        season_df = pitching_stats_bref(season)
        season_df["season"] = season
        frames.append(season_df)
    combined = pd.concat(frames, ignore_index = True)
    combined.to_parquet(cache_path, index=False)
    return combined

def extract_pitching_stats_current(force_refresh=False):
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    pull_date = date.today().isoformat()
    cache_path = os.path.join(RAW_DATA_DIR, f"pitching_stats_bref_{current_season}_asof_{pull_date}.parquet")
    if os.path.exists(cache_path) and not force_refresh:
        return pd.read_parquet(cache_path)
    df = pitching_stats_bref(current_season)
    df["season"] = current_season
    df.to_parquet(cache_path, index=False)
    return df

def extract_pitching_stats(force_refresh_current=False):
    historical = extract_pitching_stats_historical()
    current = extract_pitching_stats_current(force_refresh=force_refresh_current)
    return pd.concat([historical, current], ignore_index=True)

def extract_pitching_war(force_refresh=False):
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    pull_date = date.today().isoformat()
    cache_path = os.path.join(RAW_DATA_DIR, f"pitching_war_asof_{pull_date}.parquet")
    if os.path.exists(cache_path) and not force_refresh:
        return pd.read_parquet(cache_path)
    df=bwar_pitch(return_all=False)
    df.to_parquet(cache_path, index=False)
    return df



def _fixed_make_numeric(data):
    if data['Attendance'].count()>0:
        data['Attendance'] = data['Attendance'].str.replace(',', '')
    else:
        data['Attendance'] = np.nan
    data['Attendance'] = data['Attendance'].replace(r'^Unknown$', np.nan, regex=True)
    num_cols = ['R', 'RA', 'Inn', 'Rank', 'Attendance']
    data[num_cols]=data[num_cols].astype(float)
    return data
_team_results.make_numeric=_fixed_make_numeric

TEAM_ABBRS = ['BAL', 'BOS', 'NYY', 'TBR', 'TOR', 'CHW', 'CLE', 'DET', 'KCR', 'MIN',
              'HOU', 'LAA', 'ATH', 'SEA', 'TEX', 'ATL', 'MIA', 'NYM', 'PHI', 'WSN',
              'CHC', 'CIN', 'MIL', 'PIT', 'STL', 'ARI', 'COL', 'LAD', 'SDP', 'SFG']


def resolve_schedule_abbr(team_abbr, season):
    if team_abbr == 'ATH' and season <= 2024:
        return 'OAK'
    return team_abbr

def extract_team_season_games(team_abbr, season, force_refresh=False):
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    cache_path = os.path.join(RAW_DATA_DIR, f"games_{team_abbr}_{season}.parquet")
    if os.path.exists(cache_path) and not force_refresh:
        return pd.read_parquet(cache_path)
    br_abbr = resolve_schedule_abbr(team_abbr, season)
    df = schedule_and_record(season, br_abbr)
    df['team_abbr'] = team_abbr
    df['season'] = season
    df.to_parquet(cache_path, index=False)
    return df

def extract_games_for_season(season, force_refresh=False):
    frames = []
    for team_abbr in TEAM_ABBRS:
        frames.append(extract_team_season_games(team_abbr, season, force_refresh=force_refresh))
    return pd.concat(frames, ignore_index=True)


if __name__ == "__main__":
    df = extract_batting_stats()
    print(df.shape)
    print(df.head())
    pitch_df = extract_pitching_stats()
    print(pitch_df.shape)
    print(pitch_df.head())
    games_df = extract_games_for_season(2021)
    print(games_df.shape)
    print(games_df[['Date', 'team_abbr', 'Home_Away', 'Opp', 'W/L', 'R', 'RA']].head())