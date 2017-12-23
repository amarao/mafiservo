Workflow & terms:

- There is a game ID, which allows to join players to the same game.
- creator of the new game is a game master.
- game master set up parameters for the game (role count)
- each player joins the game by providing game ID.

- Roles:
  - civil
  - mafia
  - sheriff
  - doctor
  - girl

  Server assign roles randomly and allow player to see their role.

  1. Players decide whom to remove (day)
  2. Game master marks them as dead
  3. Game master start night.
  4. Mafia votes whom to kill (night). to kill someone all mafia members
  must enter the same number
  5. Sheriff input number and receives answer (civil/mafia)
  6. Doctor input number to heal
  7. Girl take player with herself
  8. Players wake up.
  9. Server reports kills outcome to everyone



Internals
---------
Server keep information in dict associated with game_id. Player_id
is assigned randomly at game start to different players after they
inputed a game_id. Each player is identified by cookie (which is just
  a uuid). I thought about using IP addresses, but it raises NAT issue,
  therefore I fall back to cookie.
