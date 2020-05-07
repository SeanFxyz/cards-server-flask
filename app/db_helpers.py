import sqlite3, json, secrets

def conn():
    return sqlite3.connect('cards.db')

def rowConn():
    conn = sqlite3.connect('cards.db')
    conn.row_factory = sqlite3.Row
    return conn

def dbQry(sql, *parameters):
    conn = conn()
    c = conn.cursor()
    qry = c.execute(sql, parameters).fetchall()
    conn.close()
    return qry

def dbRowQry(sql, *parameters):
    conn = rowConn()
    c = conn.cursor()
    qry = c.execute(sql, parameters).fetchall()
    conn.close()
    return qry

def dbIsPlayer(player_id):
    record = curs().execute('SELECT player_id FROM players WHERE player_id=?',
        player_id).fetchone()
    return bool(player)

def dbAddPlayer(player_name):
    conn = conn()
    c = conn.cursor()
    player_ids = []
    for record in c.execute(
            'SELECT player_id FROM players').fetchall():
        player_ids.append(record[0])

    player_id = secrets.token_urlsafe(32)
    while player_id in player_ids:
        player_id = secrets.token_urlsafe(32)

    c.execute(
            'INSERT INTO players (player_id, player_name, last_login)\
                    VALUES (?,?,?)',
            player_id, player_name, time.time())

    conn.commit().close()
    return player_id

def dbUpdatePlayer(player_id, player_name=False, last_login=False):
    conn = conn()
    c = conn.cursor()

    if player_name:
        c.execute('UPDATE players SET player_name=? WHERE player_id=?',
                player_name, player_id)
    if last_login:
        c.execute('UPDATE players SET last_login=? WHERE player_id=?',
                last_login, player_id)

    conn.commit().close()

def dbRmPlayer(player_id):
    conn = conn()
    c = conn.cursor()
    c.execute('DELETE FROM players WHERE player_id=?', player_id)
    conn.commit().close()

def dbAddGame(game_name, host_player_id):
    conn = conn()
    c = conn.cursor()
    game_ids = []
    for record in c.execute(
            'SELECT game_id FROM players').fetchall():
        game_ids.append(record[0])

    game_id = secrets.token_urlsafe(32)
    while game_id in game_ids:
        game_id = secrets.token_urlsafe(32)

    c.execute(
            'INSERT INTO games (game_id, game_name, host) VALUES (?,?,?)',
            game_id, game_name, host_player_id)

    conn.commit().close()

    return game_id

def dbRmGame(game_id):
    conn = conn()
    c = conn.cursor()
    c.execute('DELETE FROM games WHERE game_id=?', game_id).close()
    conn.commit().close()

def addSession(player_id, game_id):
    conn = conn()
    c = conn.cursor()
    c.execute('INSERT INTO sessions (player_id, game_id) VALUES (?,?)')
    conn.commit().close()
