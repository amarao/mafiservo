Mafiservo
=========

The minimalistic server to play mafia.

This server help to start to play Mafia club game without dedicated game master.
It helps to allow to run few turns before first dead player has
appeared. This player may become a game master, or all players may
continue to use this server.

This server does not provide all functions of game master: it does not count
day votes and does not restrict talk time.

It:

- assigns roles and numbers
- is tracking of dead/alive players
- allows nigh moves for Mafia, the doctor, the sheriff and the girl
    (all three are optional)
- Provides information on night results to all players at morning.


Installation
============

Pip goes here (later).

How to use
==========

Each player should use touch devices (keys are noisy and will give away
night roles) like smartphone or tablet.

Run game server. You may use any linux server (capable to run python
code) or run it on android smartphone (see installation section).

One of the players is a game master. S/he creates a new game and provides
initial settings (number of players, number of special roles). Each game
is identified by some number. Other players use 'join game' feature.

They receive unique ID (cookie), role and number. Number is public information,
role should be conceived until player death or end of the game.

At the end of the day game master input numbers of dead players and send
'night mode' command to server.

At the night mode mafia may enter number to kill. If that number matches,
mafia receive confirmation.
Sheriff enters the number and receives answer on type of a player.
Doctor marks player as 'healed'
Girl takes player with it

At each step game produces audio signal from all devices to let everyone
knew they need to do.
