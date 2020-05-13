from app import app
from flask import (render_template, render_template_string, request,
        send_from_directory, send_file, url_for)
import os, sqlite3, json, re
from enum import Enum 

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time
import atexit

from app.db_helpers import *
from app.cards_helpers import *


with open("secretkey") as keyfile:
    app.secret_key = keyfile.readline()
    keyfile.close()

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST" and request.form["player_name"]:
            player_id = dbAddPlayer(request.form["player_name"])
            return "SUCCESS\n" + player_id
    else:
        return "FAIL"

@app.route("/create", methods=["POST"])
def createGame():
    if request.method == "POST":
        game_name = request.form["game_name"]
        player_id = request.form["player_id"]
        hidden = int(request.form["hidden"])
        password = request.form["password"]
        max_players = request.form["max_players"]
        if dbIsPlayer(player_id):
            game_id = dbAddGame(game_name, player_id, hidden=hidden,
                    passwd=password, max_players=max_players)
            session_id = dbAddSession(player_id, game_id)
            return "SUCCESS\n" + game_id + '\n' + session_id
        else:
            return "FAIL\nInvalid player ID"

@app.route("/join", methods=["POST"])
def joinGame():
    if request.method == "POST":
        game_id = request.form["game_id"]
        player_id = request.form["player_id"]
        passwd = request.form["password"]
        state = dbRowQry("SELECT state FROM games WHERE game_id=?",
                game_id)[0]["state"]
        state = State(state)

        if(State(state) == State.LOBBY and
                dbCheckPass(game_id, passwd) and
                state == State.LOBBY or state == State.DISPLAY):
            session_id = dbAddSession(player_id, game_id)
            return "SUCCESS\n" + session_id
        return "FAIL"

@app.route("/games")
def getGames():
    qry = (dbRowQry("SELECT game_id, game_name, host, state FROM games \
            WHERE hidden=?", 0))
    qry_json = json.dumps([dict(row) for row in qry])
    return "SUCCESS\n" + qry_json

@app.route("/qry", methods=["POST"])
def qryGame():
    if request.method == "POST":
        session_id = request.form["session_id"]
        session_qry = dbGetSession(session_id)
        if bool(session_qry) == False:
            return "FAIL\nAuthentication failure."
        player_id = session_qry["player_id"]
        game_id = session_qry["game_id"]

        if dbIsSession(game_id, player_id):
            # Initialize the query as a copy of the game's DB record as a dict.
            qry = dict(dbGetGame(game_id))
            del qry['passwd_hash']

            # Add on player information as a dictionary with player_id values
            # as keys mapped to player_names.
            player_qry = dbQry("SELECT player_id FROM sessions WHERE game_id=?",
                    game_id)
            qry["players"] = {}
            for p in [row[0] for row in player_qry]:
                qry["players"][p] = dbPlayerName(p)

            # Add the querying player's current hand of cards to the query in
            # the form of a list of dictionaries.
            # Each dict has "card_id" mapped to a card_id and "text" mapped to
            # a list of strings (should be just one for responses).
            player_card_qry = dbRowQry("SELECT (card_id) FROM player_cards \
                    WHERE game_id=? AND player_id=?", game_id, player_id)
            player_cards = [row["card_id"] for row in player_card_qry]
            game_cards = dbRowQry("SELECT (response_id, text) FROM responses")
            card_list = [dict(row) for row in game_cards
                    if row["response_id"] in player_cards]
            qry["cards"] = card_list

            # If the game is in the selection stage and the querying player is
            # the czar, OR the game is in the display stage, add to qry["subs"]
            # a list of dict where each dict represents a player's submission.
            # "player_id" will be mapped to the player's ID and "cards" will be
            # mapped to another list of dictionaries, similar to the one
            # in qry["cards"].
            qry["subs"] = []
            if( (State(qry["state"]) == State.SELECT and
                    player_id == qry["czar"]) or
                    State(qry["state"]) == State.DISPLAY):

                sub_qry = dbRowQry("SELECT * FROM submissions WHERE game_id=?",
                        game_id)
                for row in sub_qry:
                    sub_cards = []
                    cards = json.loads(row["cards"])
                    for card in cards:
                        card_text = dbRowQry("SELECT text FROM responses \
                                WHERE response_id=?", card)[0]["text"]
                        sub_cards.append({"response_id":card, "text":card_text})

                    qry["subs"].append({
                        "player_id": row["player_id"],
                        "cards": sub_cards})

            qry_json = json.dumps(qry)
            return "SUCCESS\n" + qry_json
        
        return "FAIL\n"

@app.route("/cmd", methods=["POST"])
def command():
    if request.method == "POST":
        session_id = request.form["session_id"]
        cmd = request.form["cmd"]
        args = json.loads(request.form["args"])

        session_qry = dbGetSession(session_id)
        game_id = session_qry["game_id"]
        player_id = session_qry["player_id"]

        game = dbGetGame(game_id)
        game_state = State(game["state"])

        if cmd == "ready":
            # args is a list with one true or false value

            if(game_state != State.LOBBY and
                    game_state != State.DISPLAY):
                return "FAIL\nGame already started."
            
            checkHost()
            if args[0]:
                dbSetReady(session_id, True)
            else:
                dbSetReady(session_id, False)

            if dbAllReady(game_id):
                dbUpdateGame(game_id, {"state":State.PROMPT.value})

            return "SUCCESS"

        elif cmd == "start":
            # args is ignored

            if game["host"] != player_id:
                return "FAIL\nYou are not the host."
            if(game_state != State.LOBBY and
                    game_state != State.DISPLAY):
                return "FAIL\nGame started already."

            promptStateSetup(game_id)

            dbUpdateGame(game_id, {"selection":"", "state":State.PROMPT.value})
            return "SUCCESS"

        elif cmd == "submit":
            # args is a list of card_id values

            if game_state != State.PROMPT:
                return "FAIL\nSubmissions not open."
            if game["czar"] == player_id:
                return "FAIL\nYou are the czar."

            current_subs = dbRowQry("SELECT * FROM submissions \
                    WHERE game_id=?", game_id)

            if player_id in [row["player_id"] for row in current_subs]:
                return "FAIL\nPlayer already submitted for this round."


            dbAddSub(game_id, player_id, args)

            if len(current_subs) + 1 >= game["player_count"] - 1:
                dbUpdateGame(game_id, {"state":State.SELECT.value})

            return "SUCCESS"

        elif cmd == "select":
            # args is a list with one player_id

            if game_state != State.SELECT:
                return "FAIL\nGame not in SELECT state."
            if game["czar"] != player_id:
                return "FAIL\nYou are not the czar."
            

            sel = args[0]
            dbUpdateGame(game_id,{"selection":sel, "state":State.DISPLAY.value})

            scheduler = BackgroundScheduler()
            scheduler.add_job(func=incState, args=(game_id,), trigger="date",
                    run_date=datetime.fromtimestamp(time.time() + 15))
            scheduler.start()

            atexit.register(lambda: scheduler.shutdown())


            return "SUCCESS"
