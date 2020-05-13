Design Reflection
=================

A particularly tricky part of this project I had to deal with was figuring out how to manage all the data the server needs to keep track of. The database ended up being a little more complicated than I had originally intended.

I wasn't able to create an especially consistent and elegant system for database access. I would definitely like to improve on that in the future.

I would definitely recommend very carefully planning out how the game will progress between different states and what has to happen on the back end to reflect that progression before writing any code or designing the database.

I had the most fun with this project when I was writing my helper functions that have to assess the state of the game and players and respond accordingly by peroforming various tasks, like dealing cards to players or picking a new prompt card.

I was definitely most challenged by implementing my client application for testing. While it is at the moment just a rudimentary proof-of-concept and not a very robust client, working on that part of the project definitely hammered into my head the fact that I hadn't done the best job planning the project, and getting to the point where I was able to connect two clients and play a game took longer than it otherwise might have.

I plan to research what my other options would be aside from Flask and SQLite for how it is built (I'm looking into FastAPI, which seems to be better-optimized for this type of project), and potentially re-do it. For new features, I'm most excited about the prospect of allowing players to specify Cardcast card packs and have them automatically fetched and imported.
