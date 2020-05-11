import sqlite3, json, secrets
from hashlib import sha512

def conn():
    return sqlite3.connect("cards.db")

def rowConn():
    conn = sqlite3.connect("cards.db")
    conn.row_factory = sqlite3.Row
    return conn

# Execute SQL in sql and return list of numerically-indexed records
# Preferable for querying just one field from the DB
def dbQry(sql, *parameters):
    conn = conn()
    c = conn.cursor()
    qry = c.execute(sql, parameters).fetchall()
    conn.close()
    return qry

# Like dbQry, but each row in the list supports dict-like subscripts.
# Useful for multiple-field queries.
def dbRowQry(sql, *parameters):
    conn = rowConn()
    c = conn.cursor()
    qry = c.execute(sql, parameters).fetchall()
    conn.close()
    return qry

def dbIsPlayer(player_id):
    player = dbQry("SELECT player_id FROM players WHERE player_id=?",
            player_id)
    return bool(player)

def dbGetPlayers(game_id):
    qry = dbRowQry("SELECT * FROM players WHERE game_id=?", game_id)

def dbPlayerName(player_id):
    player_name = dbQry("SELECT player_name FROM players WHERE player_id=?",
            player_id)
    return player_name

def dbAddPlayer(player_name):
    conn = conn()
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
            player_id, player_name, time.time())

    conn.commit().close()
    return player_id

def dbUpdatePlayer(player_id, player_name=False, last_login=False):
    conn = conn()
    c = conn.cursor()

    if player_name:
        c.execute("UPDATE players SET player_name=? WHERE player_id=?",
                player_name, player_id)
    if last_login:
        c.execute("UPDATE players SET last_login=? WHERE player_id=?",
                last_login, player_id)

    conn.commit().close()

def dbRmPlayer(player_id):
    conn = conn()
    c = conn.cursor()
    c.execute("DELETE FROM players WHERE player_id=?", player_id)
    c.execute("DELETE FROM sessions WHERE player_id=?", player_id)
    conn.commit().close()

def dbAddGame(game_name, host_player_id, passwd="", hidden=0, decks=""):
    conn = conn()
    c = conn.cursor()
    game_ids = []
    for record in c.execute(
            "SELECT game_id FROM players").fetchall():
        game_ids.append(record[0])

    game_id = secrets.token_hex(4)
    while game_id in game_ids:
        game_id = secrets.token_hex(4)

    # For testing
    decks = json.dumps(["ZG5QC"])

    c.execute(
            "INSERT INTO games \
                    (game_id, game_name, host, hidden, decks) \
                    VALUES (?,?,?,?,?)",
            game_id, game_name, host_player_id, hidden, decks)

    conn.commit().close()

    return game_id

def dbGetGame(game_id):
    return dbRowQry("SELECT * FROM games WHERE game_id=?", game_id)[0]

def dbUpdateGame(game_id, data={}):
    conn = sqlite3.connect()
    c = conn.cursor()
    for a in args.keys():
        c.execute("UPDATE games SET " + a + "=? WHERE game_id=?", args[a],
                game_id)
    conn.commit().close()
    return True

def dbRmGame(game_id):
    conn = conn()
    c = conn.cursor()
    c.execute("DELETE FROM games WHERE game_id=?", game_id).close()
    conn.commit().close()

def dbAddSession(player_id, game_id):
    conn = conn()
    c = conn.cursor()
    c.execute("INSERT INTO sessions (player_id, game_id) VALUES (?,?)")
    conn.commit().close()

def dbIsSession(game_id, player_id):
    conn = rowConn()
    c = conn.cursor()
    row = c.execute("SELECT * FROM sessions WHERE game_id=? AND player_id=?",
            game_id, player_id).fetchone()
    conn.close()
    return bool(row)

def dbCheckPass(game_id, passwd):
    row = dbRowQry("SELECT (game_id, passwd_hash) FROM games WHERE game_id=?",
            game_id).fetchone()

    if row["game_id"] == game_id:
        passwd_hash = row["passwd_hash"]
        if passwd_hash:
            if(passwd_hash == 
                    sha512(str(passwd + game_id).encode()).hexdigest()):
                return True

            return False
        else:
            return True
