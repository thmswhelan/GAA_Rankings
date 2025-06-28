#Calculate GAA Rankings
import pandas as pd
import numpy as np
from datetime import datetime

# Step 1: Load gaa_results.csv into a DataFrame
# Load data
df_results = pd.read_csv("gaa_results.csv")

# Keep only selected competitions
valid_comps = [
    "Allianz Football League Roinn 1",
    "Allianz Football League Roinn 2",
    "Allianz Football League Roinn 3",
    "Allianz Football League Roinn 4",
    "Connacht GAA Football Senior Championship",
    "Leinster GAA Football Senior Championship",
    "Munster GAA Football Senior Championship",
    "Ulster GAA Football Senior Championship",
    "Tailteann Cup",
    "GAA Football All-Ireland Senior Championship"]

df_results = df_results[df_results['Competition'].isin(valid_comps)].copy()

# Convert scores like "2-14" into total points
import re

def parse_score(score_str):
    if not isinstance(score_str, str):
        return None
    match = re.match(r"^\d+-\d+$", score_str.strip())
    if not match:
        return None
    goals, points = map(int, score_str.split("-"))
    return goals * 3 + points


# Initialize team ratings
teams = pd.concat([df_results['Home Team'], df_results['Away Team']]).unique()
ratings = {team: 50 for team in teams}

# Parameters
home_advantage = 3
divisor = 10

# Determine if venue is home, away, or neutral
venue = str(row['Venue']).lower()
home_team = home.lower()
away_team = away.lower()

# Simple check: if venue contains home team name, apply advantage
if home_team in venue and away_team not in venue:
    actual_home_advantage = home_advantage
else:
    actual_home_advantage = 0  # neutral or away

# Adjust expected using actual home advantage
expected_home = 1 / (1 + 10 ** ((away_rating - (home_rating + actual_home_advantage)) / divisor))


# Elo update loop
for idx, row in df_results.iterrows():
    home = row['Home Team']
    away = row['Away Team']

    home_score = parse_score(row['Home Score'])
    away_score = parse_score(row['Away Score'])

    if home_score is None or away_score is None:
        print(f"Skipping row {idx} due to invalid score.")
        continue

    # Dynamic K factor
    competition = row['Competition']
    K = 2 if "league" in competition.lower() else 3

    # Venue logic (and home advantage)
    venue = str(row['Venue']).lower()
    home_team = home.lower()
    away_team = away.lower()
    actual_home_advantage = home_advantage if home_team in venue and away_team not in venue else 0

    # Ratings
    home_rating = ratings[home]
    away_rating = ratings[away]

    expected_home = 1 / (1 + 10 ** ((away_rating - (home_rating + actual_home_advantage)) / divisor))
    actual_home = 1 if home_score > away_score else 0

    margin_bonus = 1.5 if abs(home_score - away_score) > 8 else 0
    rating_change = round(K * margin_bonus*(actual_home - expected_home), 2)

    ratings[home] += rating_change
    ratings[away] -= rating_change

import os

# Current run date
run_date = datetime.today().strftime('%Y-%m-%d')

# Create a DataFrame: Team | Rating
df_final = pd.DataFrame(list(ratings.items()), columns=["Team", run_date])

# File to save pivoted history
output_file = "gaa_rankings_pivot.csv"

if os.path.exists(output_file):
    # Load existing file
    df_history = pd.read_csv(output_file)
    
    # Merge new column on 'Team'
    df_history = pd.merge(df_history, df_final, on="Team", how="outer")
else:
    # Start new file
    df_history = df_final

# Sort for readability
df_history.sort_values(by="Team", inplace=True)

# Save updated history
df_history.to_csv(output_file, index=False)
print("Pivoted rankings saved to gaa_rankings_pivot.csv")


