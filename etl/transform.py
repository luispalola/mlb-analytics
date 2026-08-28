import pandas as pd
import numpy as np
import re
from extract import extract_batting_stats, extract_pitching_stats, extract_batting_war, extract_pitching_war, extract_all_games

def fix_name_encoding(name):
    return name.encode('latin1').decode('unicode_escape').encode('latin1').decode('utf-8')


def build_players_dimension():
    batting = extract_batting_stats()[['mlbID', 'Name']]
    pitching = extract_pitching_stats()[['mlbID', 'Name']]
    combined = pd.concat([batting, pitching], ignore_index=True)
    combined['mlbID'] = combined['mlbID'].astype(int)
    combined = combined.drop_duplicates(subset='mlbID')
    combined['Name'] = combined['Name'].apply(fix_name_encoding)
    combined = combined.rename(columns={'mlbID': 'mlbam_id', 'Name': 'full_name'})
    return combined[['mlbam_id', 'full_name']]


def build_batting_war():
    war = extract_batting_war()
    war = war.dropna(subset=['mlb_ID'])
    war['mlb_ID'] = war['mlb_ID'].astype(int)
    war_summed = war.groupby(['mlb_ID', 'year_ID'], as_index=False)['WAR'].sum()
    war_summed = war_summed.rename(columns={'mlb_ID': 'mlbID', 'year_ID': 'season'})
    return war_summed



TEAM_ABBR_LOOKUP = {
    ('Athletics', 'AL'): 'ATH', ('Oakland', 'AL'): 'ATH',
    ('Baltimore', 'AL'): 'BAL', ('Boston', 'AL'): 'BOS',
    ('Chicago', 'AL'): 'CHW', ('Cleveland', 'AL'): 'CLE',
    ('Detroit', 'AL'): 'DET', ('Houston', 'AL'): 'HOU',
    ('Kansas City', 'AL'): 'KCR', ('Los Angeles', 'AL'): 'LAA',
    ('Minnesota', 'AL'): 'MIN', ('New York', 'AL'): 'NYY',
    ('Seattle', 'AL'): 'SEA', ('Tampa Bay', 'AL'): 'TBR',
    ('Texas', 'AL'): 'TEX', ('Toronto', 'AL'): 'TOR',
    ('Arizona', 'NL'): 'ARI', ('Atlanta', 'NL'): 'ATL',
    ('Chicago', 'NL'): 'CHC', ('Cincinnati', 'NL'): 'CIN',
    ('Colorado', 'NL'): 'COL', ('Los Angeles', 'NL'): 'LAD',
    ('Miami', 'NL'): 'MIA', ('Milwaukee', 'NL'): 'MIL',
    ('New York', 'NL'): 'NYM', ('Philadelphia', 'NL'): 'PHI',
    ('Pittsburgh', 'NL'): 'PIT', ('San Diego', 'NL'): 'SDP',
    ('San Francisco', 'NL'): 'SFG', ('St. Louis', 'NL'): 'STL',
    ('Washington', 'NL'): 'WSN',
}


def resolve_team_abbr(row):
    if ',' in row['Tm'] or ',' in row['Lev']:
        return None
    league = row['Lev'].replace('Maj-', '')
    return TEAM_ABBR_LOOKUP.get((row['Tm'], league))


def build_batting_stats():
    stats = extract_batting_stats()
    war = build_batting_war()
    merged = stats.merge(war, on=['mlbID', 'season'], how='left')
    merged['Name'] = merged['Name'].apply(fix_name_encoding)
    merged['team_abbr'] = merged.apply(resolve_team_abbr, axis=1)
    return merged



def build_pitching_war():
    war = extract_pitching_war()
    war = war.dropna(subset=['mlb_ID'])
    war['mlb_ID'] = war['mlb_ID'].astype(int)
    war_summed = war.groupby(['mlb_ID', 'year_ID'], as_index=False)['WAR'].sum()
    war_summed = war_summed.rename(columns={'mlb_ID': 'mlbID', 'year_ID': 'season'})
    return war_summed

def build_pitching_stats():
    stats = extract_pitching_stats()
    stats['mlbID'] = stats['mlbID'].astype(int)
    war = build_pitching_war()
    merged = stats.merge(war, on=['mlbID', 'season'], how='left')
    merged['Name'] = merged['Name'].apply(fix_name_encoding)
    merged['team_abbr'] = merged.apply(resolve_team_abbr, axis=1)
    merged[['W', 'L', 'SV']] = merged[['W', 'L', 'SV']].fillna(0)
    merged['ERA'] = merged['ERA'].replace([np.inf, -np.inf], np.nan)
    merged = add_fip(merged)
    return merged


def true_innings(ip):
    whole = np.floor(ip)
    outs = np.round((ip-whole)*10)
    return whole + outs/3


def add_fip(df):
    df['true_ip'] = true_innings(df['IP'])
    league = df.groupby('season').agg(
        HR=('HR', 'sum'), BB=('BB', 'sum'), HBP=('HBP', 'sum'),
        SO=('SO', 'sum'), IP=('true_ip', 'sum'), ER=('ER', 'sum'),
    ).reset_index()
    league['league_era'] = 9*league['ER'] / league['IP']
    league['fip_constant'] = league['league_era'] - (
        (13 * league['HR'] + 3 * (league['BB'] + league['HBP']) - 2 * league['SO']) / league['IP']
    )
    df = df.merge(league[['season', 'fip_constant']], on='season', how='left')
    df['FIP'] = ((13*df['HR'] + 3*(df['BB'] + df['HBP']) - 2*df['SO']) / df['true_ip']) + df['fip_constant']
    df.loc[df['true_ip'] == 0, 'FIP'] = None
    df = df.drop(columns=['true_ip'])
    return df




def parse_game_date(date_str, season):
    m = re.match(r'^(.*?)(?:\s*\((\d)\))?$', date_str.strip())
    clean_date, game_num = m.group(1).strip(), m.group(2)
    game_num = int(game_num) if game_num else 1
    parsed = pd.to_datetime(f'{clean_date}, {season}')
    return parsed.date(), game_num

def build_games():
    df = extract_all_games()
    df = df[df['Home_Away'] == 'Home'].copy()
    df = df[df['R'].notna()].copy()
    parsed = df.apply(lambda row: parse_game_date(row['Date'], row['season']), axis=1)
    df['game_date'] = parsed.apply(lambda x: x[0])
    df['game_num'] = parsed.apply(lambda x: x[1])
    df['home_team_abbr'] = df['team_abbr']
    df['away_team_abbr'] = df['Opp'].replace({'OAK' : 'ATH'})
    df['home_score'] = df['R'].astype(int)
    df['away_score'] = df['RA'].astype(int)
    return df[['game_date', 'season', 'home_team_abbr', 'away_team_abbr', 'home_score', 'away_score', 'game_num']]




if __name__ == "__main__":
    df = build_players_dimension()
    print(df.shape)
    print(df.head())