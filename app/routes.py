from app import app
from flask import (render_template, render_template_string, request,
        session, send_from_directory, send_file, url_for)
import os, sqlite3, json, re
from enum import Enum 

from app.db_helpers import *
from app.cards_helpers import *

class State(Enum):
    LOBBY = 0
    PROMPT = 1
    SELECT = 2

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

@app.route("/logout", methods=["POST"])
def logout():
    if request.method == "POST":
        dbRmPlayer(request.form["player_id"])
        return "SUCCESS"
    else:
        return "FAIL"

@app.route("/create", methods=["POST"])
def createGame():
    if request.method == "POST":
        game_name = request.form["game_name"]
        player_id = request.form["player_id"]
        hidden = int(request.form["hidden"])
        if dbIsPlayer(player_id):
            game_id = dbAddGame(game_name, player_id, hidden)
            return "SUCCESS\n" + game_id
        else:
            return "FAIL\nInvalid player ID"

@app.route("/join", methods=["POST"])
def joinGame():
    if request.method == "POST":
        game_id = request.form["game_id"]
        player_id = request.form["player_id"]
        passwd = request.form["password"]
        state = dbRowQry("SELECT state FROM games WHERE game_id=?")[0]["state"]

        if(State(state) == State.LOBBY and
                dbCheckPass(game_id, passwd) and dbIsGameOpen(game_id)):
            dbAddSession(player_id, game_id)
            return "SUCCESS"
        return "FAIL"

@app.route("/qry", methods=["POST"])
def qryGame():
    if request.method == "POST":
        game_id = request.form["game_id"]
        player_id = request.form["player_id"]
        if dbIsSession(game_id, player_id):
            qry = dict(dbGetGame(game_id))

            playerQry = dbQry("SELECT player_id FROM sessions WHERE game_id=?",
                    game_id)
            qry["players"] = {}
            for p in [row[0] for row in playerQry]:
                qry["players"][p] = dbPlayerName(p)

            cardQry = dbRowQry("SELECT (card_id, text) FROM player_cards WHERE \
                    game_id=? AND player_id=?",
                    game_id, player_id)
            qry["cards"] = [dict(row) for row in cardQry]

            if(State(qry["state"]) == State.SELECT and
                    player_id == qry["czar"]):
                qry["subs"] = dbGetSubs(game_id)

            qry_json = json.dumps(qry)
            return "SUCCESS\n" + qry_json
        
        return "FAIL\n"

@app.route("/start", methods=["POST"])
def startGame():
    if request.method == "POST":
        game_id = request.form["game_id"]
        player_id = request.form["player_id"]

        gameQry = dbGetGame(game_id)
        if gameQry["host"] == player_id:
            if State(gameQry["state"]) == State.LOBBY:
                if dbUpdateGame(game_id, {"state":State.PROMPT.value}):
                    return "SUCCESS"
                return "FAIL"
            return "FAIL\nGame already started"

        return "FAIL\nYou are not the host."

@app.route("/submit", methods=["POST"])
def submit():
    if request.method == "POST":
        game_id = request.form["game_id"]
        player_id = request.form["player_id"]
        sub = request.form["sub"]
        sub_json = json.loads(sub)

        dbAddSub(game_id, player_id, sub_json)


@app.route("/games")
def getGames():
    qry = (dbRowQry("SELECT (game_id, game_name, host, state) FROM games \
                        WHERE hidden=?", 0))
    qry_json = json.dumps([dict(row) for row in qry])
    return "SUCCESS\n" + qry_json
