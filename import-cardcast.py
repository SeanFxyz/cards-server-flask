import sys, json, sqlite3

# Imports specified deck code from decks/ directory

deck_id = sys.argv[1]
deck = "decks/" + deck_id

deck_info={}
deck_cards={}

with open(deck + "_info.json") as infofile:
    deck_info = json.load(infofile)
    infofile.close()

with open(deck + "_cards.json") as cardfile:
    deck_cards = json.load(cardfile)
    cardfile.close()

conn = sqlite3.connect('cards.db')
c = conn.cursor()

c.execute("INSERT INTO decks (\
        deck_id,\
        name,\
        description,\
        unlisted,\
        created_at,\
        updated_at,\
        external_copyright,\
        copyright_holder_url,\
        category,\
        call_count,\
        response_count,\
        author_id,\
        rating)\
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (deck_info["code"],
        deck_info["name"],
        deck_info["description"],
        deck_info["unlisted"],
        deck_info["created_at"],
        deck_info["updated_at"],
        deck_info["external_copyright"],
        deck_info["copyright_holder_url"],
        deck_info["category"],
        deck_info["call_count"],
        deck_info["response_count"],
        deck_info["author"]["id"],
        deck_info["rating"]))

for card in deck_cards["calls"]:
    c.execute("INSERT INTO calls (\
            call_id,\
            text,\
            created_at,\
            nsfw,\
            deck_id)\
            VALUES (?,?,?,?,?)",
            (card["id"],
            json.dumps(card["text"]),
            card["created_at"],
            int(card["nsfw"]),
            deck_id))

for card in deck_cards["responses"]:
    c.execute("INSERT INTO responses (\
            response_id,\
            text,\
            created_at,\
            nsfw,\
            deck_id)\
            VALUES (?,?,?,?,?)",
            (card["id"],
            json.dumps(card["text"]),
            card["created_at"],
            int(card["nsfw"]),
            deck_id))


conn.commit()
conn.close()
