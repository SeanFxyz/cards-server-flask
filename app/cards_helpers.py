import sqlite3, json
from random import randrange
from math import ceil

from app.db_helpers import *

def deal(game_id, hand_size):
    game_qry = dbGetGame(game_id)
    game_decks = json.loads(game_qry["decks"])

    game_responses = []
    for deck in game_decks:
        card_qry = dbRowQry("SELECT * FROM responses WHERE deck_id=?", deck)
        game_responses += [card["response_id"] for card in card_qry]

    player_card_qry = dbRowQry("SELECT * FROM player_cards WHERE \
            game_id=?", game_id)

    game_player_cards = [card["card_id"] for card in player_card_qry]

    session_qry = dbRowQry("SELECT * FROM sessions WHERE game_id=?", game_id)
    players = [row["player_id"] for row in session_qry]

    for player_id in players:
        new_cards = []
        card_count = len([card["card_id"] for card in player_card_qry
                    if card["player_id"] == player_id])
        while card_count < hand_size:
            candidate = game_responses[randrange(len(game_responses))]
            while candidate in game_player_cards:
                candidate = game_responses[randrange(len(game_responses))]

            new_cards.append(candidate)
            card_count += 1

        for card_id in new_cards:
            dbAddPlayerCard(game_id, player_id, card_id)

def checkHost(game_id):
    game_data = dbGetGame(game_id)
    
    session_data = dbRowQry("SELECT * FROM sessions \
            WHERE game_id=?", game_id)

    if len([row for row in session_data
            if row["player_id"] == game_data["host"]]) == 0:
        new_host_id = session_data[randint(0, len(session_data))]["player_id"]
        dbUpdateGame(game_id, {"host": new_host_id})

def promptStateSetup(game_id):


    game_qry = dbGetGame(game_id)
    game_decks = json.loads(game_qry["decks"])

    deal(game_id, game_qry["hand_size"])

    session_qry = dbRowQry("SELECT * FROM sessions WHERE game_id=?", game_id)
    players = [row["player_id"] for row in session_qry]
    czar_i = 0
    for n in range(1, len(players)):
        if players[n] == game_qry["czar"]:
            czar_i = n

    new_czar = players[czar_i]

    dbUpdateGame(game_id, {"czar":players[n]})

    game_calls = []
    for deck in game_decks:
        card_qry = dbRowQry("SELECT * FROM calls WHERE deck_id=?", deck)
        game_calls += [card["text"] for card in card_qry]
    
    new_prompt = game_calls[randrange(len(game_calls))]

    cards_req = ceil(len(json.loads(new_prompt)) / 2)
    
    dbUpdateGame(game_id,
            {
                "current_prompt":new_prompt,
                "cards_req":cards_req,
                "czar":new_czar
                })
