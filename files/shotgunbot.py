from espn_api.football import League, Team
from dataclasses import dataclass
from sys import maxsize
from random import randrange
import os
import requests
from openai import OpenAI

# Environment variables
GROUPME_ACCESS_TOKEN = os.getenv("GROUPME_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ESPN_S2 = os.getenv("ESPN_S2")
SWID = "{" + str(os.getenv("SWID")) + "}"

GROUPME_API_BASE = "https://api.groupme.com/v3"

@dataclass
class KickerInfo:
    score: int
    name: str

def get_message(losers: list[tuple[Team, KickerInfo]]) -> str:
    client = OpenAI(api_key=OPENAI_API_KEY)

    user_input = ""
    for loser in losers:
        user_input += (
            f"{loser[0].team_name}'s kicker, {loser[1].name}, scored {loser[1].score} points this week. "
            f"{loser[0].team_name}'s owner is {loser[0].owners[0]['firstName']} {loser[0].owners[0]['lastName']}. "
        )

    system_prompt = (
        "Your name is shotgunbot. You are in charge of writing a message for a fantasy football league. "
        "The message should be about the kicker who scored the least points in the previous week. "
        "The message should be funny and make fun of the kicker's poor performance and mention that the team's owner must shotgun a beer. "
        "The message will be sent immediately, so don't add any placeholders or things for me to fill in later. "
        "Use the provided information to create a humorous message. "
        "Ensure the team's owner's name is included in the message at least once, exactly as I provide it, with first and last name. "
        "If I mention multiple owners, there was a tie this week. "
        "Keep the message short. Just a few sentences at most."
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0.8,
    )

    return response.choices[0].message.content

def get_kicker_message() -> str:
    l = League(
        league_id=1070340,
        year=2025,
        espn_s2=ESPN_S2,
        swid=SWID,
    )

    last_week = l.current_week - 1
    team_to_kicker_points: dict[Team, KickerInfo] = {}
    min_kicker_points = maxsize

    for score in l.box_scores(last_week):
        home_kicker = [p for p in score.home_lineup if p.slot_position == "K"]
        away_kicker = [p for p in score.away_lineup if p.slot_position == "K"]

        if home_kicker:
            home_kicker_info = KickerInfo(round(home_kicker[0].points, 1), home_kicker[0].name)
        else:
            home_kicker_info = KickerInfo(0, "YOU DIDN'T PLAY A KICKER")

        if away_kicker:
            away_kicker_info = KickerInfo(round(away_kicker[0].points, 1), away_kicker[0].name)
        else:
            away_kicker_info = KickerInfo(0, "YOU DIDN'T PLAY A KICKER")

        team_to_kicker_points[score.home_team] = home_kicker_info
        team_to_kicker_points[score.away_team] = away_kicker_info

        min_kicker_points = min(min_kicker_points, home_kicker_info.score, away_kicker_info.score)

    losers: list[tuple[Team, KickerInfo]] = []
    for team, kicker_info in team_to_kicker_points.items():
        if kicker_info.score == min_kicker_points:
            losers.append((team, kicker_info))

    if losers:
        return get_message(losers)
    else:
        raise ValueError("Cannot find loser. This is probably a bug")

# ------------------ GroupMe HTTP functions ------------------

def get_group_members(group_id: str):
    url = f"{GROUPME_API_BASE}/groups/{group_id}?token={GROUPME_ACCESS_TOKEN}"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()["response"]
    return data["members"]

def post_group_message(group_id: str, text: str, mentions=None):
    url = f"{GROUPME_API_BASE}/groups/{group_id}/messages?token={GROUPME_ACCESS_TOKEN}"

    payload = {"message": {"text": text}}
    if mentions:
        payload["message"]["attachments"] = [
            {"type": "mentions", "loci": [m[0] for m in mentions], "user_ids": [m[1] for m in mentions]}
        ]

    resp = requests.post(url, json=payload)
    print(resp.text)
    resp.raise_for_status()
    return resp.json()

def post_message(message: str):
    target_group_id = '15618258'

    # Get members for mentions
    members = get_group_members(target_group_id)

    # Build mentions list [( [start_idx, length], user_id ), ...]
    message_lower = message.lower()
    mentions = []
    for m in members:
        name_last = m["nickname"].split(' ')[-1].lower()
        idx = message_lower.find(name_last)
        if idx != -1:
            mentions.append(([idx, len(name_last)], m["user_id"]))

    post_group_message(target_group_id, message, mentions=mentions if mentions else None)

# ------------------ Run bot ------------------

def run_shotgunbot():
    kicker_message = get_kicker_message()
    full_message = 'SHOTGUNBOT: ' + kicker_message
    post_message(full_message)

if __name__ == '__main__':
    run_shotgunbot()
