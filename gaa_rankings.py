#Calculate GAA Rankings
import pandas as pd
import numpy as np
from datetime import datetime

# Step 1: Load gaa_results.csv into a DataFrame
df_results = pd.read_csv('gaa_results.csv')

# Convert scores like "2-14" into total points
def parse_score(score_str):
    goals, points = map(int, score_str.split("-"))
    return goals * 3 + points

# Initialize team ratings
teams = pd.concat([df_results['Home Team'], df_results['Away Team']]).unique()
ratings = {team: 50 for team in teams}

# Parameters
K = 3
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

    home_rating = ratings[home]
    away_rating = ratings[away]

    expected_home = calculate_expected(home_rating, away_rating)
    actual_home = 1 if home_score > away_score else 0

    # Margin of victory bonus
    margin_bonus = 1.5 if abs(home_score - away_score) > 8 else 0

    # Calculate and round change
    rating_change = round(K * margin_bonus * (actual_home - expected_home), 2)

    # Update ratings
    ratings[home] += rating_change
    ratings[away] -= rating_change

# Save final rankings
df_final = pd.DataFrame(list(ratings.items()), columns=["Team", "Rating"])
df_final.sort_values(by="Rating", ascending=False, inplace=True)
df_final.to_csv("gaa_elo_rankings_final.csv", index=False)

print("Rankings saved to gaa_elo_rankings_final.csv")

