import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import subprocess
import os

# Today's date
today = datetime.today()
general_file = "gaa_results.csv"

# Target URL
url = "https://www.gaa.ie/fixtures-results"
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")
    match_details = soup.find_all("div", class_="gar-match-item")

    rows_to_append = []
    for match in match_details:
        home_team = match.find("div", class_="gar-match-item__team -home")
        away_team = match.find("div", class_="gar-match-item__team -away")
        competition = match.find_previous("h3", class_="gar-matches-list__group-name")
        competition_name = competition.get_text(strip=True) if competition else "Unknown Competition"
        match_date = match.get("data-match-date", "No date available")
        venue = match.find("div", class_="gar-match-item__venue")
        venue_name = venue.get_text(strip=True).replace('Venue:', '').strip() if venue else "No venue available"
        # Get and format the match date
        raw_date = match.get("data-match-date", None)
        if raw_date:
            try:
            parsed_date = datetime.fromisoformat(raw_date)
            match_date = parsed_date.strftime("%d/%m/%Y")
            except ValueError:
            match_date = "Invalid date"
        else:
        match_date = "No date available"
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

        home_team_name = home_team.get_text(strip=True) if home_team else "Unknown"
        away_team_name = away_team.get_text(strip=True) if away_team else "Unknown"

        row = [competition_name, home_team_name, away_team_name, match_date, venue_name, home_score, away_score]
        rows_to_append.append([excel_safe(v) for v in row])

    # Write to main file (append mode)
    append_header = not os.path.exists(general_file)
    with open(general_file, mode='a', newline='', encoding='utf-8') as gen_file:
        gen_writer = csv.writer(gen_file)
        if append_header:
            gen_writer.writerow(["Competition", "Home Team", "Away Team", "Date", "Venue", "Home Score", "Away Score"])
        gen_writer.writerows(rows_to_append)

    print(f"✅ Appended {len(rows_to_append)} rows to '{general_file}'.")

    # Git commit & push
    subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@users.noreply.github.com"])
    subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"])
    subprocess.run(["git", "add", general_file])
    subprocess.run(["git", "commit", "-m", f"Update GAA results for {today.strftime('%Y-%m-%d')}"])
    subprocess.run(["git", "push"])

else:
    print("❌ Failed to retrieve the page. Status Code:", response.status_code)

