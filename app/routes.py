from app import app
from flask import (render_template, render_template_string, request,
        session, send_from_directory, send_file, url_for)
import os, sqlite3, json, re

from db_helpers import *
from cards_helpers import *

with open('secretkey') as keyfile:
    app.secret_key = keyfile.readline()
    keyfile.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session and session['player_id']:
        return session['player_id']
    elif request.method == 'POST' and request.form['player_name']:
            player_id = dbAddPlayer(request.form['player_name'])
            session['player_id'] = player_id
            return 'SUCCESS\n' + player_id
    else:
        return 'FAIL'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and dbIsPlayer(request.form['player_id']):
        session['player_id'] = request.form['player_id']
        dbUpdatePlayer(request.form['player_id'], last_login=time.time())
        return 'SUCCESS\n'
    else:
        return 'FAIL'

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST' and request.form['player_id']:
        dbRmPlayer(request.form['player_id'])

@app.route('/create', methods=['GET', 'POST'])
def createGame():
    if request.method == 'POST':
        game_name = request.form['game_name']
        if(session and session['player_id']
                and dbIsPlayer(session['player_id'])):
            player_id = request.form['player_id']
            game_id = dbAddGame(game_name, player_id)
            return 'SUCCESS\n' + game_id


@app.route('/games')
def games():
