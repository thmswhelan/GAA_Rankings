#Calculate GAA Rankings
import pandas as pd
import numpy as np
import re
from datetime import datetime

# Step 1: Load gaa_results.csv into a DataFrame
df_results = pd.read_csv('gaa_results.csv')

# Initialize a DataFrame for rankings with starting rank of 50 for each county
teams = pd.concat([df_results['Home Team'], df_results['Away Team']]).unique()
df_rankings = pd.DataFrame({'Team': teams, 'Ranking': 50})
