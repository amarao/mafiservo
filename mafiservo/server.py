import random
import math
from flask import Flask
from flask import render_template, request, redirect
from . import game

app = Flask('mafiservo')
games = {}


def new_game_id():
    '''
        If we have less than 10 active games:
            random number from 10 to 99,
        less than 100:
            random number from 100 to 999
        less than 1000:
            random number from 1000 to 9999
        ...etc
    '''
    global games
    game_id_range = 10 ** (math.ceil(math.log(len(games) + 2, 10)) + 1)
    while True:
        game_id = random.choice(range(int(game_id_range/10), game_id_range))
        if game_id not in games:
            return game_id


def set_cookie_and_game_redirect(game_id, player_id, hash):
    resp = redirect('/game.html')
    resp.set_cookie(
        'game',
        "%s+%s+%s" % (game_id, player_id, hash),
        expires=24 * 3600
    )
    return resp


@app.route('/')
def menu():
    notfound = (b'notfound' in request.query_string)
    badid = (b'bad_id' in request.query_string)
    return render_template("index.html", notfound=notfound, badid=badid)


@app.route('/join.html', methods=['POST'])
def new():
    global games
    game_id = int(request.form['game_id'])
    if game_id not in games:
        return redirect('/?notfound')

    game_cookie = request.cookies.get('game')
    if game_cookie:
        cookie_game, player_id, hash = game_cookie.split('.')
        if cookie_game == game_id:
            try:
                games[game_id].rejoin()
            except game.JoinError:
                resp = redirect('/?bad_id')
                resp.set_cookie('game', '', expires=0)
            return set_cookie_and_game_redirect(game_id, player_id, hash)
    player_id, hash = games[game_id].join()
    return set_cookie_and_game_redirect(game_id, player_id, hash)


@app.route('/new.html', methods=['POST'])
def join():
    global games
    total = int(request.form['total'])
    mafia = int(request.form['mafia'])
    sheriff = bool(request.form['sheriff'])
    doctor = bool(request.form['doctor'])
    girl = bool(request.form['girl'])
    new_game = game.Game(total, mafia, sheriff, doctor, girl)
    game_id = new_game_id()
    games[game_id] = new_game
    player_id, hash = games[game_id].join()
    return set_cookie_and_game_redirect(game_id, player_id, hash)
