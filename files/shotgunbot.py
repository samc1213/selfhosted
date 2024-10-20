from espn_api.football import League, Team
from dataclasses import dataclass
from sys import maxsize
from random import randrange
from groupy.client import Client
from groupy import attachments
import os

PALTRY_SYNONYMS = [
    "small",
    "meager",
    "trifling",
    "insignificant",
    "negligible",
    "inadequate",
    "insufficient",
    "scant",
    "scanty",
    "derisory",
    "pitiful",
    "pitiable",
    "pathetic",
    "miserable",
    "sorry",
    "wretched",
    "puny",
    "trivial",
    "beggarly",
    "mean",
    "ungenerous",
    "inappreciable",
    "mere",
    "measly",
    "piddling",
    "piffling",
    "mingy",
    "dinky",
    "poxy",
    "exiguous",
]

GROUPME_ACCESS_TOKEN=os.getenv("GROUPME_ACCESS_TOKEN")
ESPN_S2=os.getenv("ESPN_S2")
SWID= "{" + os.getenv("SWID") + "}"

@dataclass
class KickerInfo:
    score: int
    name: str


def get_paltry_synonym() -> str:
    return PALTRY_SYNONYMS[randrange(len(PALTRY_SYNONYMS))]


def get_message(loser: tuple[Team, KickerInfo]) -> str:
    return f"{loser[0].team_name} ({loser[0].owners[0]['firstName']} {loser[0].owners[0]['lastName']})'s kicker, {loser[1].name}, put up a {get_paltry_synonym()} {loser[1].score} points this week. Time to shotgun!"


def get_kicker_message() -> str:
    l = League(
        league_id=1070340,
        year=2024,
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

    if len(losers) == 1:
        loser = losers[0]
        return get_message(loser)
    elif len(losers) > 1:
        message = ""
        first_time = True
        for loser in losers:
            if first_time:
                prepend = ""
            else:
                prepend = "\n"
            message += prepend + get_message(loser)

            first_time = False
        return message
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
