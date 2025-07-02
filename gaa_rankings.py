# Calculate GAA Rankings
import pandas as pd
import numpy as np
import re
from datetime import datetime
import os
import subprocess
import sys


# Load match results
df_results = pd.read_csv("gaa_results.csv", encoding="ISO-8859-1")
df_venues = pd.read_csv("venue_county_list.csv", encoding="ISO-8859-1")
venue_to_county = dict(zip(df_venues['Venue'].str.lower().str.strip(), df_venues['County']))

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
    "GAA Football All-Ireland Senior Championship",
]
df_results = df_results[df_results['Competition'].isin(valid_comps)].copy()

# Parse scores
def parse_score(score_str):
    if not isinstance(score_str, str) or not re.match(r"^\d+-\d+$", score_str.strip()):
        print(f"❌ Invalid score format: '{score_str}'")
        sys.exit(1)
    goals, points = map(int, score_str.strip().split("-"))
    return goals * 3 + points


# Initialize ratings from the second column of gaa_rankings_pivot.csv
ratings = {}

pivot_file = "gaa_rankings_pivot.csv"
if os.path.exists(pivot_file):
    df_pivot = pd.read_csv(pivot_file)
    if df_pivot.shape[1] >= 2:
        initial_col = df_pivot.columns[1]  # second column (e.g., "01/01/2025")
        ratings = dict(zip(df_pivot["Team"], df_pivot[initial_col]))
        print(f"✅ Initialized ratings from column: {initial_col}")
    else:
        print("⚠️ Pivot file does not have a second column. Falling back to default rating of 50.")
else:
    print("⚠️ Pivot file not found. Initializing ratings to 50.")
    teams = pd.concat([df_results['Home Team'], df_results['Away Team']]).unique()
    ratings = {team: 50 for team in teams}

divisor = 10

# Elo update loop
for idx, row in df_results.iterrows():
    home = row["Home Team"]
    away = row["Away Team"]
    home_score = parse_score(row['Home Score'])
    away_score = parse_score(row['Away Score'])

    if home_score is None or away_score is None:
        print(f"Skipping row {idx} due to invalid score.")
        continue

    if home not in ratings:
    print(f"❌ Team '{home}' not found in initial ratings.")
    sys.exit(1)
    if away not in ratings:
    print(f"❌ Team '{away}' not found in initial ratings.")
    sys.exit(1)

    home_rating = ratings[home]
    away_rating = ratings[away]

    venue = str(row.get("Venue", "")).lower().strip()
    if venue not in venue_to_county:
    print(f"❌ Venue '{venue}' not found in venue list.")
    sys.exit(1)

    venue_county = venue_to_county.get(venue)
    home_advantage = 2 if venue_county == home else 0

    # Expected score
    expected_home = 1 / (1 + 10 ** ((away_rating - (home_rating + home_advantage)) / divisor))
    if home_score == away_score:
        actual_home = 0.5
    elif home_score > away_score:
        actual_home = 1
    else:
        actual_home = 0
        
    # Competition-based K
    competition = row["Competition"]
    K = 2 if "league" in competition.lower() else 3

    # Margin bonus
    margin_bonus = 1.5 if abs(home_score - away_score) > 8 else 1.0

    rating_change = round(K * margin_bonus * (actual_home - expected_home), 2)

    ratings[home] += rating_change
    ratings[away] -= rating_change

# Save pivoted rating history
run_date = datetime.today().strftime('%Y-%m-%d')
df_final = pd.DataFrame(
    [(team, round(rating, 2)) for team, rating in ratings.items()],
    columns=["Team", run_date]
)


output_file = "gaa_rankings_pivot.csv"
# Remove duplicate date column if it exists
if os.path.exists(output_file):
    df_history = pd.read_csv(output_file)
    if run_date in df_history.columns:
        df_history.drop(columns=[run_date], inplace=True)
    df_history = pd.merge(df_history, df_final, on="Team", how="outer")
else:
    df_history = df_final

df_history.sort_values("Team", inplace=True)
df_history.to_csv(output_file, index=False)

# Git commit & push
subprocess.run(["git", "add", output_file])
subprocess.run(["git", "commit", "-m", f"Update rankings for {run_date}"])
subprocess.run(["git", "push"])


print("Pivoted rankings saved to gaa_rankings_pivot.csv")



