import random
import math
import time
from flask import Flask
from flask import render_template, request, redirect, abort
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


def process_cookie():
    game_cookie = request.cookies.get('game')
    if game_cookie:
        game_name, player_id, hash = game_cookie.split('+')
        return int(game_name), int(player_id), hash


def set_cookie_and_game_redirect(game_id, player_id, hash):
    resp = redirect('/game.html')
    resp.set_cookie(
        'game',
        "%s+%s+%s" % (game_id, player_id, hash),
        expires=int(time.time()) + 24 * 3600
    )
    return resp


@app.route('/')
def menu():
    notfound = (b'notfound' in request.query_string)
    badid = (b'bad_id' in request.query_string)
    return render_template("index.html", notfound=notfound, badid=badid)


@app.route('/join.html', methods=['POST'])
def join():
    global games
    game_id = int(request.form['game_id'])
    if game_id not in games:
        return redirect('/?notfound')

    game_cookie = request.cookies.get('game')
    if game_cookie:
        cookie_game, player_id, hash = game_cookie.split('+')
        if cookie_game == game_id:
            try:
                games[game_id].rejoin()
            except game.JoinError:
                resp = redirect('/?bad_id')
                resp.set_cookie('game', '', expires=0)
            return set_cookie_and_game_redirect(game_id, player_id, hash)
    player_id, hash = games[game_id].join()
    return set_cookie_and_game_redirect(game_id, player_id, hash)


@app.route('/new.html', methods=['GET'])
def new_game_dialog():
    return render_template('new.html')


@app.route('/new.html', methods=['POST'])
def new():
    global games
    total = int(request.form['total'])
    mafia = int(request.form['mafia'])
    sheriff = bool(request.form.get('sheriff', True))
    doctor = bool(request.form.get('doctor', True))
    girl = bool(request.form.get('girl', False))
    try:
        new_game = game.Game(total, mafia, sheriff, doctor, girl)
    except game.BadSettings as e:
        return render_template('invalid.html', error=e)
    game_id = new_game_id()
    games[game_id] = new_game
    player_id, hash = games[game_id].join()
    resp = set_cookie_and_game_redirect(game_id, player_id, hash)
    resp.set_cookie('control', new_game.control, expires=2**31)
    return resp


@app.route('/game.html', methods=['POST', 'GET'])
def main_game():
    global games
    game_id, player_id, hash = process_cookie()
    if game_id not in games:
        return render_template(
            'invalid.html',
            error="Game with ID %s is not found" % game_id
        )
    the_game = games[game_id]
    if the_game.players[player_id].hash != hash:
        abort(403)
    if (b'die' in request.query_string):
        the_game.die(player_id)
        return redirect('/dead.html')
    if the_game.game_status() != "Game in progress":
        return render_template("end.html")
    if not the_game.players[player_id].is_alive:
        return redirect('/dead.html')
    if not the_game.is_ready():
        return redirect('/not_ready.html')
    control = (games[game_id].control == request.cookies.get('control'))
    player = games[game_id].players[player_id]
    resp = render_template(
        'game.html', control=control, player=player, game=games[game_id])
    return resp


@app.route('/dead.html', methods=['GET'])
def dead():
    global games
    game_id, player_id, hash = process_cookie()
    if game_id not in games:
        abort(403)
    if games[game_id].players[player_id].hash != hash:
        abort(403)
    if games[game_id].players[player_id].is_alive:
        return redirect('/game.html')
    the_game = games[game_id]
    return render_template(
        "dead.html",
        game=the_game,
        player=the_game.players[player_id],
        alive=len(list(the_game.list_alive())),
        total=len(the_game.players),
        refresh=15
    )


@app.route('/end.html', methods=['POST', 'GET'])
def end_game():
    global games
    game_id, player_id, hash = process_cookie()
    if game_id not in games:
        abort(403)
    if games[game_id].players[player_id].hash != hash:
        abort(403)
    if games[game_id].game_status() == "Game in progress":
        return redirect('/game.html')
    return render_template(
        "end.html",
        game=games[game_id],
        player=games[game_id].players[player_id]
    )


@app.route('/not_ready.html', methods=['GET'])
def not_ready():
    global games
    game_id, player_id, hash = process_cookie()
    if game_id not in games:
        return render_template(
            'invalid.html',
            error="Game with ID %s is not found" % game_id
        )
    the_game = games[game_id]
    if the_game.players[player_id].hash != hash:
        abort(403)
    if the_game.is_ready():
        return redirect('/game.html')
    return render_template('not_ready.html', refresh=5)
