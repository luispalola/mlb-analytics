CREATE TABLE teams (
    team_id SERIAL PRIMARY KEY,
    team_abbr VARCHAR(5) UNIQUE NOT NULL,
    team_name VARCHAR(100) NOT NULL,
    league VARCHAR(10),
    division VARCHAR(20)
);


CREATE TABLE players (
    player_id SERIAL PRIMARY KEY,
    mlbam_id INT UNIQUE,
    fangraphs_id INT,
    full_name VARCHAR(100) NOT NULL,
    bats CHAR(1),
    throws CHAR(1),
    debut_date DATE
);


CREATE TABLE games (
    game_id SERIAL PRIMARY KEY,
    game_date DATE NOT NULL,
    season INT NOT NULL,
    home_team_id INT REFERENCES teams(team_id),
    away_team_id INT REFERENCES teams(team_id),
    home_score INT,
    away_score INT,
    venue VARCHAR(100),
    game_number SMALLINT NOT NULL DEFAULT 1,
    UNIQUE (game_date, home_team_id, away_team_id, game_number)
);

CREATE INDEX idx_games_season ON games (season);


CREATE TABLE batting_stats (
    batting_stat_id SERIAL PRIMARY KEY,
    player_id INT REFERENCES players(player_id),
    team_id INT REFERENCES teams(team_id),
    season INT NOT NULL,
    games_played INT,
    plate_appearances INT,
    at_bats INT,
    hits INT,
    doubles INT,
    triples INT,
    home_runs INT,
    rbi INT,
    walks INT,
    strikeouts INT,
    stolen_bases INT,
    avg NUMERIC(4,3),
    obp NUMERIC(4,3),
    slg NUMERIC(4,3),
    ops NUMERIC(4,3),
    war NUMERIC(4,1),
    data_as_of DATE NOT NULL DEFAULT CURRENT_DATE,
    UNIQUE (player_id, season)
);


CREATE TABLE pitching_stats (
    pitching_stat_id SERIAL PRIMARY KEY,
    player_id INT REFERENCES players(player_id),
    team_id INT REFERENCES teams(team_id),
    season INT NOT NULL,
    wins INT,
    losses INT,
    era NUMERIC(6,2),
    games INT,
    games_started INT,
    innings_pitched NUMERIC(5,1),
    strikeouts INT,
    walks INT,
    whip NUMERIC(6,3),
    fip NUMERIC(6,2),
    war NUMERIC(4,1),
    data_as_of DATE NOT NULL DEFAULT CURRENT_DATE,
    UNIQUE (player_id, season)
);


CREATE TABLE statcast_game_summary (
    id SERIAL PRIMARY KEY,
    game_id INT REFERENCES games(game_id),
    player_id INT REFERENCES players(player_id),
    avg_exit_velo NUMERIC(5,2),
    avg_launch_angle NUMERIC(5,2),
    barrel_pct NUMERIC(5,2),
    hard_hit_pct NUMERIC(5,2)
);