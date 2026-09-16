from datetime import datetime
from flask import Flask, jsonify
import requests

app = Flask(__name__)

LEAGUES = [
    {
        "name": "NFL",
        "url": (
            "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
        ),
    },
    {
        "name": "NCAA FB",
        "url": (
            "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard"
        ),
    },
    {
        "name": "MLB",
        "url": (
            "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"
        ),
    },
    {
        "name": "NBA",
        "url": (
            "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
        ),
    },
    {
        "name": "NHL",
        "url": (
            "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard"
        ),
    },
    {
        "name": "NCAA BB",
        "url": (
            "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard"
        ),
    },
    {
        "name": "WNBA",
        "url": (
            "https://site.api.espn.com/apis/site/v2/sports/basketball/wnba/scoreboard"
        ),
    },
    {
        "name": "MLS",
        "url": (
            "https://site.api.espn.com/apis/site/v2/sports/soccer/usa.1/scoreboard"
        ),
    },
]

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


@app.route("/")
def get_sports():
  # Rotate sports every 2 minutes based on system clock
  total_minutes = int(datetime.utcnow().timestamp() / 60)
  start_index = (total_minutes // 2) % len(LEAGUES)

  for attempts in range(len(LEAGUES)):
    current_index = (start_index + attempts) % len(LEAGUES)
    league = LEAGUES[current_index]

    try:
      res = requests.get(league["url"], headers=headers, timeout=5)
      if res.status_code == 200:
        data = res.json()
        events = data.get("events", [])

        if events:
          target_game = None

          # 1. Look for a live game
          for game in events:
            if game["competitions"][0]["status"]["type"]["state"] == "in":
              target_game = game
              break

          # 2. If no live game, look for an upcoming game
          if not target_game:
            for game in events:
              if game["competitions"][0]["status"]["type"]["state"] == "pre":
                target_game = game
                break

          # 3. Fallback to the first game
          if not target_game:
            target_game = events[0]

          comp = target_game["competitions"][0]
          t1 = comp["competitors"][0]["team"]["abbreviation"]
          t2 = comp["competitors"][1]["team"]["abbreviation"]
          state = comp["status"]["type"]["state"]
          status_detail = comp["status"]["type"]["detail"]

          if state == "pre":
            line1 = f"[{league['name']}] {t1} vs {t2}"
            line2 = f"Starts: {status_detail}"
          else:
            s1 = comp["competitors"][0].get("score", "0")
            s2 = comp["competitors"][1].get("score", "0")
            line1 = f"[{league['name']}] {t1} {s1}-{s2} {t2}"
            line2 = status_detail

          return jsonify({"line1": line1, "line2": line2})
    except Exception as e:
      print(f"Error fetching {league['name']}: {e}")

  return jsonify(
      {"line1": "SPORTS TICKER", "line2": "No Active Games Today"}
  )


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=10000)
