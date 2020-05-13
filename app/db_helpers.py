import sqlite3, json, secrets, time
from hashlib import sha512

def connect():
    return sqlite3.connect("cards.db")

def rowConnect():
    conn = sqlite3.connect("cards.db")
    conn.row_factory = sqlite3.Row
    return conn

# Execute SQL in sql and return list of numerically-indexed records
# Preferable for querying just one field from the DB
def dbQry(sql, *parameters):
    conn = connect()
    c = conn.cursor()
    qry = c.execute(sql, parameters).fetchall()
    conn.close()
    return qry

# Like dbQry, but each row in the list supports dict-like subscripts.
# Useful for multiple-field queries.
def dbRowQry(sql, *parameters):
    conn = rowConnect()
    c = conn.cursor()
    qry = c.execute(sql, parameters).fetchall()
    conn.close()
    return qry

def dbAddPlayerCard(game_id, player_id, card_id):
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO player_cards (game_id, player_id, card_id) \
            VALUES (?, ?, ?)", (game_id, player_id, card_id))
    conn.commit()
    conn.close

def dbIsPlayer(player_id):
    player = dbQry("SELECT player_id FROM players WHERE player_id=?",
            player_id)
    return bool(player)

def dbAddSub(game_id, player_id, sub=[]):
    conn = connect()
    c = conn.cursor()
    cards = json.dumps(sub)
    c.execute("INSERT INTO submissions (game_id, player_id, cards) \
            VALUES (?,?,?)", (game_id, player_id, cards))
    for card_id in sub:
        c.execute("DELETE FROM player_cards \
                WHERE game_id=? AND player_id=? AND card_id=?",
                (game_id, player_id, card_id))
    conn.commit()
    conn.close

def dbGameOver(game_id):
    conn = connect()
    c = conn.cursor()
    for table in [
            games,
            player_cards,
            sessions,
            submissions]:
        c.execute("DELETE FROM ? WHERE game_id=?", table, game_id)

    conn.commit()
    conn.close()

def dbGetPlayers(game_id):
    qry = dbRowQry("SELECT * FROM players WHERE game_id=?", game_id)

def dbClearSubs(game_id):
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM submissions WHERE game_id=?", (game_id,))
    conn.commit()
    conn.close()

def dbPlayerName(player_id):
    player_name = dbQry("SELECT player_name FROM players WHERE player_id=?",
            player_id)[0][0]
    return player_name

def dbAddPlayer(player_name):
    conn = connect()
    c = conn.cursor()
    player_ids = []
    for record in c.execute(
            "SELECT player_id FROM players").fetchall():
        player_ids.append(record[0])

    player_id = secrets.token_urlsafe(32)
    while player_id in player_ids:
        player_id = secrets.token_urlsafe(32)

    c.execute(
            "INSERT INTO players (player_id, player_name, last_login) \
                    VALUES (?,?,?)",
            (player_id, player_name, time.time()))

    conn.commit()
    conn.close
    return player_id

def dbUpdatePlayer(player_id, player_name=False, last_login=False):
    conn = connect()
    c = conn.cursor()

    if player_name:
        c.execute("UPDATE players SET player_name=? WHERE player_id=?",
                (player_name, player_id))
    if last_login:
        c.execute("UPDATE players SET last_login=? WHERE player_id=?",
                (last_login, player_id))

    conn.commit()
    conn.close

def dbRmPlayer(player_id):
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM players WHERE player_id=?", player_id)
    c.execute("DELETE FROM sessions WHERE player_id=?", player_id)
    conn.commit()
    conn.close

def dbAddGame(game_name, host_player_id, passwd="", hidden=0, decks="",
        max_players=2):
    conn = connect()
    c = conn.cursor()
    id_qry = c.execute("SELECT game_id FROM games").fetchall()
    game_ids = [row[0] for row in id_qry]

    game_id = secrets.token_hex(4)
    while game_id in game_ids:
        game_id = secrets.token_hex(4)

    # For testing
    decks = json.dumps(["ZG5QC"])

    c.execute(
            "INSERT INTO games \
                    (game_id, game_name, host, hidden, decks, state, \
                    max_players) \
                    VALUES (?,?,?,?,?,?,?)",
            (game_id, game_name, host_player_id, hidden, decks, 0, max_players))

    conn.commit()
    conn.close

    return game_id

def dbGetGame(game_id):
    return dbRowQry("SELECT * FROM games WHERE game_id=?", game_id)[0]

def dbSetReady(session_id, ready):
    conn = connect()
    c = conn.cursor()
    if ready:
        c.execute("UPDATE sessions SET ready=1 \
                WHERE session_id=?", session_id)
    else:
        c.execute("UPDATE sessions SET ready=0 \
                WHERE session_id=?", session_id)
    conn.commit()
    conn.close()

def dbUpdateGame(game_id, data={}):
    conn = connect()
    c = conn.cursor()
    for k in data.keys():
        c.execute("UPDATE games SET " + k + "=? WHERE game_id=?",
                (data[k], game_id))
    conn.commit()
    conn.close
    return True

def dbRmGame(game_id):
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM games WHERE game_id=?", game_id).close()
    conn.commit()
    conn.close

def dbAddSession(player_id, game_id):
    conn = connect()
    c = conn.cursor()
    session_id = secrets.token_urlsafe(32)
    c.execute("INSERT INTO sessions (session_id, player_id, game_id) \
            VALUES (?,?,?)", (session_id, player_id, game_id))

    # Update player_count
    player_count = c.execute("SELECT player_count FROM games \
            WHERE game_id=?", (game_id,)).fetchone()[0]
    player_count += 1
    c.execute("UPDATE games SET player_count=? WHERE game_id=?",
            (player_count, game_id))

    conn.commit()
    conn.close()
    return session_id

def dbIsSession(game_id, player_id):
    conn = rowConnect()
    c = conn.cursor()
    row = c.execute("SELECT * FROM sessions WHERE game_id=? AND player_id=?",
            (game_id, player_id)).fetchone()
    conn.close()
    return bool(row)

def dbGetSession(session_id):
    conn = rowConnect()
    c = conn.cursor()
    qry = c.execute("SELECT * FROM sessions WHERE session_id=?", (session_id,))
    row = qry.fetchone()
    conn.close()
    return row

def dbCheckPass(game_id, passwd):
    row = dbRowQry("SELECT game_id, passwd_hash FROM games WHERE game_id=?",
            game_id)[0]

    if row["game_id"] == game_id:
        passwd_hash = row["passwd_hash"]
        if passwd_hash:
            if(passwd_hash == 
                    sha512(str(passwd + game_id).encode()).hexdigest()):
                return True

            return False
        else:
            return True
