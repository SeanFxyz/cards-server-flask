import sqlite3

# Cleans up the database.

conn = sqlite3.connect('cards.db')
c = conn.cursor()
c.execute("DELETE FROM games")
c.execute("DELETE FROM players")
c.execute("DELETE FROM sessions")
c.execute("DELETE FROM player_cards")
c.execute("DELETE FROM submissions")
conn.commit()
conn.close()
