# gaa_scraper.py

import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import subprocess

# -------------------------------
# Scraping GAA Matches
# -------------------------------

# Today's date for filename
today = datetime.today()
filename = f"gaa_matches_{today.strftime('%Y-%m')}.csv"

# URL for GAA fixtures page
url = "https://www.gaa.ie/fixtures-results"

# Send HTTP request to fetch the page content
response = requests.get(url)

# Check if request was successful
if response.status_code == 200:
    page_content = response.content
    soup = BeautifulSoup(page_content, "html.parser")

    # Prepare CSV file to save the data
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Competition", "Home Team", "Away Team", "Date", "Venue", "Home Score", "Away Score"])

        match_details = soup.find_all("div", class_="gar-match-item")

        for match in match_details:
            home_team = match.find("div", class_="gar-match-item__team -home")
            away_team = match.find("div", class_="gar-match-item__team -away")
            competition = match.find_previous("h3", class_="gar-matches-list__group-name")
            competition_name = competition.get_text(strip=True) if competition else "Unknown Competition"
            match_date = match.get("data-match-date", "No date available")
            venue = match.find("div", class_="gar-match-item__venue")
            venue_name = venue.get_text(strip=True).replace('Venue:', '').strip() if venue else "No venue available"

            scores = match.find_all("div", class_="gar-match-item__score")
            if len(scores) == 2:
                home_score = scores[0].get_text(strip=True)
                away_score = scores[1].get_text(strip=True)
            else:
                home_score = "N/A"
                away_score = "N/A"

            if '-' not in home_score or '-' not in away_score:
                home_score = "Invalid score"
                away_score = "Invalid score"

            if home_team and away_team:
                home_team_name = home_team.get_text(strip=True)
                away_team_name = away_team.get_text(strip=True)
            else:
                home_team_name = "Unknown"
                away_team_name = "Unknown"

            writer.writerow([competition_name, home_team_name, away_team_name, match_date, venue_name, home_score, away_score])

    print(f"Data saved to '{filename}'.")

    # -------------------------------
    # Auto commit & push to GitHub
    # -------------------------------

    subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@users.noreply.github.com"])
    subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"])
    subprocess.run(["git", "add", filename])
    subprocess.run(["git", "commit", "-m", f"Add GAA matches scrape for {today.strftime('%Y-%m-%d')}"])
    subprocess.run(["git", "push"])

else:
    print("Failed to retrieve the page. Status Code:", response.status_code)
