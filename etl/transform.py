import pandas as pd
from extract import extract_batting_stats, extract_pitching_stats

def fix_name_encoding(name):
    return name.encode('latin1').decode('unicode_escape').encode('latin1').decode('utf-8')


def build_players_dimension():
    batting = extract_batting_stats()[['mlbID', 'Name']]
    pitching = extract_pitching_stats()[['mlbID', 'Name']]
    combined = pd.concat([batting, pitching], ignore_index=True)
    combined = combined.drop_duplicates(subset='mlbID')
    combined['Name'] = combined['Name'].apply(fix_name_encoding)
    combined = combined.rename(columns={'mlbID': 'mlbam_id', 'Name': 'full_name'})
    return combined[['mlbam_id', 'full_name']]

if __name__ == "__main__":
    df = build_players_dimension()
    print(df.shape)
    print(df.head())