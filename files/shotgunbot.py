from espn_api.football import League, Team
from dataclasses import dataclass
from sys import maxsize
from random import randrange
from groupy.client import Client
from groupy import attachments
import os
from openai import OpenAI


GROUPME_ACCESS_TOKEN=os.getenv("GROUPME_ACCESS_TOKEN")
ESPN_S2=os.getenv("ESPN_S2")
SWID= "{" + str(os.getenv("SWID")) + "}"

@dataclass
class KickerInfo:
    score: int
    name: str


def get_message(losers: list[tuple[Team, KickerInfo]]) -> str:
    client = OpenAI()
    
    input = ""
    for loser in losers:
        input += f"{loser[0].team_name}'s kicker, {loser[1].name}, scored {loser[1].score} points this week. {loser[0].team_name}'s owner is {loser[0].owners[0]['firstName']} {loser[0].owners[0]['lastName']}. "

    response = client.responses.create(
        model="gpt-4o",
        instructions="Your name is shotgunbot. You are in charge of writing a message for a fantasy football league. The message should be about the kicker who scored the least points in the previous week. The message should be funny and make fun of the kicker's poor performance and mention that the team's owner must shotgun a beer. The message will be sent immediately, so don't add any placeholders or things for me to fill in later. Use the provided information to create a humorous message. Ensure the team's owner's name is included in the message at least one, exactly as I provide it, with first and last name. If I mention multiple owners, there was a tie this week. You may look up information online about the last week in the NFL if needed.",
        input=input,
    )

    return response.output_text


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
            home_kicker_info = KickerInfo(
                round(home_kicker[0].points, 1), home_kicker[0].name
            )
        else:
            home_kicker_info = KickerInfo(0, "YOU DIDNT PLAY A KICKER")
        if away_kicker:
            away_kicker_info = KickerInfo(
                round(away_kicker[0].points, 1), away_kicker[0].name
            )
        else:
            away_kicker_info = KickerInfo(0, "YOU DIDNT PLAY A KICKER")

        team_to_kicker_points[score.home_team] = home_kicker_info
        team_to_kicker_points[score.away_team] = away_kicker_info

        if home_kicker_info.score < min_kicker_points:
            min_kicker_points = home_kicker_info.score

        if away_kicker_info.score < min_kicker_points:
            min_kicker_points = away_kicker_info.score

    losers: list[tuple[Team, KickerInfo]] = []
    for team, kicker_info in team_to_kicker_points.items():
        if kicker_info.score == min_kicker_points:
            losers.append((team, kicker_info))

    if len(losers) >= 1:
        return get_message(losers)
    else:
        raise ValueError("Cannot find loser. This is probably a bug")

def post_mesage(message: str):
    client = Client.from_token(GROUPME_ACCESS_TOKEN)
    for group in client.groups.list_all():
        if 'group_id' in group.data and group.data['group_id'] == '15618258':
            name_to_user_id = {m.nickname.split(' ')[-1]: m.user_id for m in group.members}
            message_lower = message.lower()
            loci = []
            user_ids = []
            for name, user_id in name_to_user_id.items():
                name_idx = message_lower.find(name.lower())
                if name_idx != -1:
                    loci.append([name_idx, len(name)])
                    user_ids.append(user_id)
            group.post(text=message, attachments=[attachments.Mentions(loci=loci, user_ids=user_ids)])



def run_shotgunbot():
    kicker_message = get_kicker_message()
    full_message = 'SHOTGUNBOT: ' + kicker_message
    post_mesage(message=full_message)

if __name__ == '__main__':
    run_shotgunbot()
