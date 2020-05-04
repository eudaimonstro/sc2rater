from __future__ import print_function
import io
import pickle
import os.path
import time
import sys
import getopt
import re

from pprint import pprint

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import sc2reader
from trueskill import Rating, rate, rate_1vs1, quality_1vs1

from player import Player

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']


def main(argv):
    test_flag = False
    help_message = """
    Available options are:
        -h help: Help (display this message)
        -t test: Run a test on a single replay"
        """
    try:
        opts, args = getopt.getopt(argv, "ht", ["help", "test"])
    except getopt.GetoptError:
        print(help_message)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print("Available options are:\n\t-h help: Help (display this message)\n\t-t test: Run a test on a single replay")
            sys.exit()
        elif opt in ("-t"):
            test_flag = True
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    steve = Player("steve")
    ryan = Player("ryan")
    kevin = Player("kevin")
    stephen = Player("stephen")
    laura = Player("laura")
    j = Player("j")
    colin = Player("colin")
    bo = Player("bo")
    george = Player("george")
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
        "RyGuyChiGuy": ryan,
        "Rowsdower": stephen,
        "EggshellJoe": j,
        "CouchSixNine": steve,
        "GrandQuizzer": steve,
        "cdudeRising": colin,
        "coldpockets": laura,
        "FlankRight": george,
        "A.I. (Very Easy)": ai_very_easy,
        "A.I. (Easy)": ai_easy,
        "A.I. (Medium)": ai_medium,
        "A.I. (Hard)": ai_hard,
        "A.I. (Harder)": ai_harder,
        "A.I. (Very Hard)": ai_very_hard,
        "A.I. (Elite)": ai_elite,
        "A.I. (Insane)": ai_insane
    }

    replay_folder_id = '1ddE90f7JP1YA19l2Reh65s74xV-0mKTP'

    page_token = None
    replay_file_ids = []
    while True:
        response = service.files().list(
            q=f"'{replay_folder_id}' in parents",
            fields="nextPageToken, files(id)",
            pageToken=page_token).execute()
        response_list = response['files']
        if test_flag:
            response_list = response_list[:5]
        for f_id in response_list:
            replay_file_ids.append(f_id)
        if test_flag:
            break
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break

    l = len(replay_file_ids)
    printProgressBar(0, l, prefix='Progress:',
                     suffix='Complete', length=50)
    replays = []
    for i, file in enumerate(replay_file_ids):
        replay_bytes = service.files().get_media(
            fileId=file['id']).execute()
        replay = io.BytesIO(replay_bytes)
        printProgressBar(i + 1, l, prefix='Loading Replays:',
                         suffix='Complete', length=50)
        replays.append(sc2reader.load_replay(replay))

    replays = sorted(replays, key=lambda x: x.unix_timestamp)

    history = []
    for replay in replays:
        rating_groups = []
        pprint(f"Teams: {replay.teams}")
        if len(replay.teams[0].players) is 0 or len(replay.teams[1].players) is 0 or (len(replay.teams) is 2 and len(replay.teams[0].players) is 1 and len(replay.teams[1].players) is 1 and (not replay.teams[0].players[0].is_human or not replay.teams[1].players[0].is_human)):
            continue
        for team in replay.teams:
            ratings_group = {}
            for p in team.players:
                if p.is_human and p.name in players:
                    ratings_group[p] = getattr(
                        players[p.name], p.play_race.lower())
                elif not p.is_human:
                    ratings_group[p] = getattr(
                        players[f"A.I. ({p.difficulty})"], p.play_race.lower())
                else:
                    break
            if team.result == 'Win':
                rating_groups.insert(0, ratings_group)
            else:
                rating_groups.append(ratings_group)

        rated_rating_groups = rate(rating_groups)
        for i, team in enumerate(rated_rating_groups):
            pprint(f"i: {i}, team: {team}")
            for player, rating in team.items():
                if player.is_human:
                    setattr(players[player.name],
                            player.play_race.lower(), rating)
                else:
                    setattr(players[f"A.I. ({player.difficulty})"],
                            player.play_race.lower(), rating)

        history.append(rated_rating_groups)
        pprint(rated_rating_groups)


def graph_history(self, history):
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


if __name__ == '__main__':
    main(sys.argv[1:])
