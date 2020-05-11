import sqlite3, json

from app.db_helpers import *

def deal(game_id, hand_size):
    gameQry = dbGetGame(game_id)
    game_decks = json.loads(gameQry["decks"])

    game_responses = []
    for deck in game_decks:
        card_qry = dbRowQry("SELECT * FROM responses WHERE deck_id=?", deck_id)
        game_responses += [dict(card) for card in card_qry]

    players = [row["player_id"] for row in dbGetPlayers(game_id)]
    hands = {}
    for player_id in players:
        h = []
        while len(h) < hand_size:
            taken_cards = dbRowQry("SELECT card_id FROM player_cards \
                    WHERE game_id=?, player_id=?", game_id, player_id)
            new_card = 
            while 
