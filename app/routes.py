from app import app
from flask import (render_template, render_template_string, request,
        session, send_from_directory, send_file, url_for)
import os, sqlite3, json, re

from app.db_helpers import *
from app.cards_helpers import *

with open('secretkey') as keyfile:
    app.secret_key = keyfile.readline()
    keyfile.close()

@app.route('/login', methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and request.form['player_name']:
            player_id = dbAddPlayer(request.form['player_name'])
            return 'SUCCESS\n' + player_id
    else:
        return 'FAIL'

@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST' and request.form['player_id']:
        dbRmPlayer(request.form['player_id'])
        return 'SUCCESS'
    else:
        return 'FAIL'

@app.route('/create', methods=['POST'])
def createGame():
    if request.method == 'POST':
        game_name = request.form['game_name']
        player_id = request.form['player_id']
        if dbIsPlayer(player_id):
            game_id = dbAddGame(game_name, player_id)
            return 'SUCCESS\n' + game_id
        else:
            return 'FAIL\nInvalid player ID'

@app.route('/qry', methods=['POST'])
def qryGame():
    if request.method == 'POST':
        game_id = request.form['game_id']
        qry = dict(dbRowQry('SELECT * FROM games WHERE game_id=?', game_id)[0])
        qry_json = json.dumps(qry)
        return 'SUCCESS\n' + qry_json
