import pandas as pd
from extract import extract_batting_stats, extract_pitching_stats, extract_batting_war

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



if __name__ == "__main__":
    df = build_players_dimension()
    print(df.shape)
    print(df.head())