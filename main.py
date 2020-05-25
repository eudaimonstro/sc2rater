from __future__ import print_function
import io
import pickle
import os.path
import time
import random
import sys
import getopt
import re
import filecmp
import glob
import csv
import itertools

from operator import itemgetter, attrgetter
from datetime import datetime
from pprint import pprint

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import sc2reader
from trueskill import Rating, rate, rate_1vs1, quality_1vs1

from player import Player

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

steve = Player("steve")
ryan_s = Player("ryan_s")
kevin = Player("kevin")
stephen = Player("stephen")
laura = Player("laura")
j = Player("j")
colin = Player("colin")
bo = Player("bo")
george = Player("george")
ryan_k = Player("ryan_k")
ai_very_easy = Player("ai very easy")
ai_easy = Player("ai easy")
ai_medium = Player("ai medium")
ai_hard = Player("ai hard")
ai_harder = Player("ai harder")
ai_very_hard = Player("ai very hard")
ai_elite = Player("ai elite")
ai_insane = Player("ai insane")

players = {
    "PRhumperdink": bo,
    "OldSock": kevin,
    "RyGuyChiGuy": ryan_s,
    "Rowsdower": stephen,
    "EggshellJoe": j,
    "CouchSixNine": steve,
    "GrandQuizzer": steve,
    "cdudeRising": colin,
    "coldpockets": laura,
    "FlankRight": george,
    "RedOrm": ryan_k,
    "A.I. (Very Easy)": ai_very_easy,
    "A.I. (Easy)": ai_easy,
    "A.I. (Medium)": ai_medium,
    "A.I. (Hard)": ai_hard,
    "A.I. (Harder)": ai_harder,
    "A.I. (Very Hard)": ai_very_hard,
    "A.I. (Elite)": ai_elite,
    "A.I. (Insane)": ai_insane
}


def main(argv):
    test_flag = False
    help_message = """
    Available options are:
        -h help: Help (display this message)
        -t test: Run a test on a single replay"
        """

    sc2reader.configure(
        depth=1
    )

    replays = sc2reader.load_replays(
        '/home/steve/starcraft_replays', load_level=2)

    history = {
        "steve": {
            "protoss": [],
            "terran": [],
            "zerg": []
        },
        "ryan_s": {
            "protoss": [],
            "terran": [],
            "zerg": []
        },
        "kevin": {
            "protoss": [],
            "terran": [],
            "zerg": []
        },
        "stephen": {
            "protoss": [],
            "terran": [],
            "zerg": []
        },
        "laura": {
            "protoss": [],
            "terran": [],
            "zerg": []
        },
        "j": {
            "protoss": [],
            "terran": [],
            "zerg": []
        },
        "colin": {
            "protoss": [],
            "terran": [],
            "zerg": []
        },
        "bo": {
            "protoss": [],
            "terran": [],
            "zerg": []
        },
        "george": {
            "protoss": [],
            "terran": [],
            "zerg": []
        },
        "ryan_k": {
            "protoss": [],
            "terran": [],
            "zerg": []
        },
        "ai_very_easy": {
            "protoss": [],
            "terran": [],
            "zerg": []
        },
        "ai_easy": {
            "protoss": [],
            "terran": [],
            "zerg": []
        },
        "ai_medium": {
            "protoss": [],
            "terran": [],
            "zerg": []
        },
        "ai_hard": {
            "protoss": [],
            "terran": [],
            "zerg": []
        },
        "ai_harder": {
            "protoss": [],
            "terran": [],
            "zerg": []
        },
        "ai_very_hard": {
            "protoss": [],
            "terran": [],
            "zerg": []
        },
        "ai_elite": {
            "protoss": [],
            "terran": [],
            "zerg": []
        },
        "ai_insane": {
            "protoss": [],
            "terran": [],
            "zerg": []
        }
    }

    valid_replay_length = 0

    sorted_replays = sorted(replays, key=attrgetter('unix_timestamp'))

    for replay in sorted_replays:
        pprint(
            f"Date: {datetime.utcfromtimestamp(replay.unix_timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
        pprint(f"Teams: {replay.teams}")
        if replay.winner is None:
            pprint("No winner found?")
            continue
        pprint(f"Winner: {replay.winner.players}")
        rating_groups = []
        if not check_if_valid_teams(replay):
            continue
        for team in replay.teams:
            ratings_group = {}
            for p in team.players:
                if p.is_human and p.name in players:
                    ratings_group[p] = getattr(
                        players[p.name], p.play_race.lower()).current_trueskill
                elif not p.is_human:
                    ratings_group[p] = getattr(
                        players[f"A.I. ({p.difficulty})"], p.play_race.lower()).current_trueskill
                else:
                    break
            if team.result == 'Win':
                rating_groups.insert(0, ratings_group)
            else:
                rating_groups.append(ratings_group)
        if len(ratings_group) > 1:
            rated_rating_groups = rate(rating_groups)
        else:
            continue
        valid_replay_length += 1
        for i, team in enumerate(rated_rating_groups):
            for player, rating in team.items():
                if player.is_human:
                    player_race = getattr(
                        players[player.name], player.play_race.lower())
                else:
                    player_race = getattr(players[f"A.I. ({player.difficulty})"],
                                          player.play_race.lower())
                player_race.current_trueskill = rating

        history["steve"]["protoss"].append(steve.protoss)
        history["steve"]["terran"].append(steve.terran)
        history["steve"]["zerg"].append(steve.zerg)
        history["ryan_s"]["protoss"].append(ryan_s.protoss)
        history["ryan_s"]["terran"].append(ryan_s.terran)
        history["ryan_s"]["zerg"].append(ryan_s.zerg)
        history["kevin"]["protoss"].append(kevin.protoss)
        history["kevin"]["terran"].append(kevin.terran)
        history["kevin"]["zerg"].append(kevin.zerg)
        history["stephen"]["protoss"].append(stephen.protoss)
        history["stephen"]["terran"].append(stephen.terran)
        history["stephen"]["zerg"].append(stephen.zerg)
        history["laura"]["protoss"].append(laura.protoss)
        history["laura"]["terran"].append(laura.terran)
        history["laura"]["zerg"].append(laura.zerg)
        history["j"]["protoss"].append(j.protoss)
        history["j"]["terran"].append(j.terran)
        history["j"]["zerg"].append(j.zerg)
        history["colin"]["protoss"].append(colin.protoss)
        history["colin"]["terran"].append(colin.terran)
        history["colin"]["zerg"].append(colin.zerg)
        history["bo"]["protoss"].append(bo.protoss)
        history["bo"]["terran"].append(bo.terran)
        history["bo"]["zerg"].append(bo.zerg)
        history["george"]["protoss"].append(george.protoss)
        history["george"]["terran"].append(george.terran)
        history["george"]["zerg"].append(george.zerg)
        history["ryan_k"]["protoss"].append(ryan_k.protoss)
        history["ryan_k"]["terran"].append(ryan_k.terran)
        history["ryan_k"]["zerg"].append(ryan_k.zerg)
        history["ai_very_easy"]["protoss"].append(ai_very_easy.protoss)
        history["ai_very_easy"]["terran"].append(ai_very_easy.terran)
        history["ai_very_easy"]["zerg"].append(ai_very_easy.zerg)
        history["ai_easy"]["protoss"].append(ai_easy.protoss)
        history["ai_easy"]["terran"].append(ai_easy.terran)
        history["ai_easy"]["zerg"].append(ai_easy.zerg)
        history["ai_medium"]["protoss"].append(ai_medium.protoss)
        history["ai_medium"]["terran"].append(ai_medium.terran)
        history["ai_medium"]["zerg"].append(ai_medium.zerg)
        history["ai_hard"]["protoss"].append(ai_hard.protoss)
        history["ai_hard"]["terran"].append(ai_hard.terran)
        history["ai_hard"]["zerg"].append(ai_hard.zerg)
        history["ai_harder"]["protoss"].append(ai_harder.protoss)
        history["ai_harder"]["terran"].append(ai_harder.terran)
        history["ai_harder"]["zerg"].append(ai_harder.zerg)
        history["ai_very_hard"]["protoss"].append(ai_very_hard.protoss)
        history["ai_very_hard"]["terran"].append(ai_very_hard.terran)
        history["ai_very_hard"]["zerg"].append(ai_very_hard.zerg)
        history["ai_elite"]["protoss"].append(ai_elite.protoss)
        history["ai_elite"]["terran"].append(ai_elite.terran)
        history["ai_elite"]["zerg"].append(ai_elite.zerg)
        history["ai_insane"]["protoss"].append(ai_insane.protoss)
        history["ai_insane"]["terran"].append(ai_insane.terran)
        history["ai_insane"]["zerg"].append(ai_insane.zerg)

    for player in history:
        ax_num = 0
        fig = plt.figure(figsize=(12, 12))
        for race in ["protoss", "terran", "zerg"]:
            ax_num += 1
            ax = fig.add_subplot(3, 1, ax_num)
            ax.set(xlim=(1, valid_replay_length + 1), ylim=(0, 50))
            ax.set_ylabel('TrueSkill')
            ax.plot(range(0, valid_replay_length),
                    list(map(lambda x: x.current_trueskill, history[player][race])), label=f"{player} as {race}")
            ax.set_title(f"{player} as {race}")
            pprint(
                f"{player} as {race} TrueSkill mu: {round(history[player][race][-1].current_trueskill.mu, 2)}, sigma: {round(history[player][race][-1].current_trueskill.sigma, 2)}")
        fig.savefig(f"plots/{player.replace(' ', '_')}")

    try:
        opts, args = getopt.getopt(argv, "", ["help",
                                              "test",
                                              "steve=",
                                              "ryan_s=",
                                              "ryan_k=",
                                              "colin=",
                                              "bo=",
                                              "j=",
                                              "laura=",
                                              "kevin=",
                                              "stephen=",
                                              "george="
                                              ])
    except getopt.GetoptError:
        print(help_message)
        sys.exit(2)

    players_array = []

    for opt, arg in opts:
        if opt in ("--steve"):
            player_name = "steve"
        elif opt in ("--ryan_s"):
            player_name = "ryan_s"
        elif opt in ("--ryan_k"):
            player_name = "ryan_k"
        elif opt in ("--colin"):
            player_name = "colin"
        elif opt in ("--bo"):
            player_name = "bo"
        elif opt in ("--j"):
            player_name = "j"
        elif opt in ("--laura"):
            player_name = "laura"
        elif opt in ("--kevin"):
            player_name = "kevin"
        elif opt in ("--stephen"):
            player_name = "stephen"
        elif opt in ("--george"):
            player_name = "george"
        if arg == "protoss":
            player_race = "protoss"
        elif arg == "terran":
            player_race = "terran"
        elif arg == "zerg":
            player_race = "zerg"
        players_array.append({"name": player_name, "race": player_race, "rating": getattr(
            globals()[player_name], player_race).current_trueskill})

    total_sum = sum(map(lambda x: x['rating'].mu, players_array))
    teams = []
    for i in range(1, len(players_array)):
        combinations = itertools.combinations(players_array, i)
        for combo in combinations:
            for player in combo:
                print(f"{player['name']} {player['race']}", end=", ")
            team_1_sum = sum(map(lambda x: x['rating'].mu, combo))
            print(team_1_sum)
            team_2_sum = total_sum - team_1_sum
            difference = team_1_sum - team_2_sum
            print(f"Difference: {difference}")
            teams.append({'team': (list(map(lambda x: x['name'], combo)), list(map(
                lambda x: x['race'], combo))), 'difference': abs(difference)})
    sorted_teams = sorted(teams, key=lambda x: x['difference'])
    for i, team in enumerate(sorted_teams):
        if i % 2 == 0:
            print(
                f"Team {int((i / 2) + 1)}: {sorted_teams[i]['team']}, difference: {sorted_teams[i]['difference']}")


def check_if_valid_teams(replay):
    if len(replay.teams) == 1:
        return False
    if len(replay.teams[0].players) == 0 or len(replay.teams[1].players) == 0:
        return False
    if (
        len(replay.teams) == 2
        and len(replay.teams[0].players) == 1
        and len(replay.teams[1].players) == 1
        and (
            not replay.teams[0].players[0].is_human
            or not replay.teams[1].players[0].is_human
        )
    ):
        return False
    for team in replay.teams:
        for player in team.players:
            if not check_if_player_is_us_or_computer(player):
                return False
    return True


def check_if_player_is_us_or_computer(player):
    if player.is_human:
        return player.name in players
    else:
        return True


def replay_exists(replay, replays):
    for r in replays:
        if r == replay:
            return True
    return False


def graph_history(history):
    x = np.linspace(1, len(history), 1)
    fig, ax = plt.subplots()
    for player in players:
        player_history = map(lambda x: x[player.name], history)
        ax.plot(x, history, label=f"{player.name} Terran")


def sort_replays(elem):
    return elem.unix_timestamp


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 *
                                                     (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def makeRequestWithExponentialBackoff(request):
    """Wrapper to request Google Analytics data with exponential backoff.
    The makeRequest method accepts the analytics service object, makes API
    requests and returns the response. If any error occurs, the makeRequest
    method is retried using exponential backoff.
    Args:
        analytics: The analytics service object
    Returns:
        The API response from the makeRequest method.
    """
    for n in range(0, 5):
        try:
            return request.execute()

        except:
            time.sleep((2 ** n) + random.random())

    print("There has been an error, the request never succeeded.")


if __name__ == '__main__':
    main(sys.argv[1:])
