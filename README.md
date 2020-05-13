A flask-based server for a Cards Against Humanity/Apples-to-Apples -style call-response game

Clients in progress:
* https://github.com/SeanaldSeanson/cards-cli.git

Interface
=========

Clients interact with the server through HTTP POST requests to the following routes:

(This is subject to change. I am planning to remove the /login route and alter the /create and /join routes so that `player_id` values are never used as a form of authentication, and expand the use of `session_id` values accordingly.)


/login
------
### Form data:
* `player_name`: the connecting client's desired player name.

Registers a new player ID for the user and returns the randomly generated `player_id` value. This is currently a requred step before joining/creating a game, but will probably be phased out.


/create
-------
### Form data:
* `player_id`: The connecting player's `player_id`. This will be made the created game's `host` field value.
* `game_name`: The desired `game_name`. Need not be unique.
* `password`: The desired password for the game. Can be empty. Not well tested.

Creates a new game and automatically joins the player to the created game. Returns the `game_id` and the player's `session_id`.


/join
-----
### Form data:
* `player_id`: The player's `player_id`.
* `game_id`: The `game_id` of the game to join.

Joins connecting player to an existing game. Returns a new `session_id`.


/games
------
Accepts a GET request, returns all existing games as a list of dictionaries encoded to JSON.


/qry
----
### Form data:
* `session_id`
* `game_id`

Takes a `session_id` as authentication and returns a JSON-encoded data structure with the following layout:
'''
Keys:
    game_id: str
    game_name: str
    host: str (a player_id)
    hidden: int (0 or 1)
    state: int (represents a state from the State Enum in cards_helpers.py)
    current_prompt: str (a call_id value from calls table)
    player_count: int
    max_players: int
    czar: str (a player_id)
    cards_req: int (cards required for current prompt)
    decks: str (JSON-encoded list of deck_id values for decks enabled in this game)
    selection: str (a player_id, indicates czar's current selected submission)
    hand_size: int (the size of each player's hand of cards for this game)

    players: dict (maps player_ids to player_names)

    cards: list of dict
        Keys:
            response_id: str (response_id from responses table)
            text: str (JSON-encoded list of strings)

    subs: list of dict (current player submissions)
        Keys:
            player_id: str
            cards: list of dict (like 'cards' key above)
                Keys:
                    response_id: str
                    text: str (JSON-encoded list of strings)
'''

/cmd
----
### Form data:
* `session_id`
* `cmd`: A command string
* `args`: A JSON list of arguments to the command.

Authenticates the `session_id` and runs the command specified by `cmd` with the given `args`. Current (working) commands are:
* `start`: Only works for the host player, moves the game from the lobby stage to the prompt stage.
* `submit`: For everyone but the current czar, submits a list of `response_id` values from `args` as the player's submissions for the round.
* `select`: For the current czar, selects the czar's favorite submission, based on a single `player_id` value provided in `args`
