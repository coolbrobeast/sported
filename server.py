from flask import Flask, jsonify
import requests

app = Flask(__name__)

# All major sports endpoints on ESPN
LEAGUES = [
    (
        "NFL",
        "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard",
    ),
    (
        "CFB",
        (
            "http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard"
        ),
    ),
    (
        "NBA",
        (
            "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
        ),
    ),
    (
        "MLB",
        "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard",
    ),
    (
        "NHL",
        "http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard",
    ),
]

current_index = 0


@app.route("/ticker")
def ticker():
  global current_index
  headers = {"User-Agent": "Mozilla/5.0"}

  # Loop through leagues to find one with active games today
  attempts = 0
  while attempts < len(LEAGUES):
    league_name, url = LEAGUES[current_index]
    # Rotate to the next sport for the subsequent request
    current_index = (current_index + 1) % len(LEAGUES)
    attempts += 1

    try:
      res = requests.get(url, headers=headers, timeout=4)
      if res.status_code == 200:
        data = res.json()
        events = data.get("events", [])
        if events:
          # Grab the first game of this sport
          game = events[0]
          competition = game["competitions"][0]
          competitors = competition["competitors"]

          team1 = competitors[0]["team"]["abbreviation"]
          score1 = competitors[0].get("score", "0")
          team2 = competitors[1]["team"]["abbreviation"]
          score2 = competitors[1].get("score", "0")

          score_line = f"[{league_name}] {team1} {score1}-{score2} {team2}"
          status_detail = competition["status"]["type"]["detail"]

          return jsonify({"line1": score_line, "line2": status_detail})
    except Exception as e:
      print(f"Error fetching {league_name}: {e}")
      continue

  return jsonify({"line1": "ALL SPORTS", "line2": "No Live Games Right Now"})


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)