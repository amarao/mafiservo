from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from . import game

app = Flask('mafiservo')
games = {}


@app.route('/')
def menu():
    notfound = (b'notfound' in request.query_string)
    return render_template("index.html", notfound=notfound)


@app.route('/new.html', methods=['POST'])
def new():
    global games
    game_id = request.form['game_id']
    if game_id not in games:
        return redirect('/?notfound')
    game_cookie = request.cookies.get('game')
    if game_cookie:
        game, player_id = game_cookie.split('.')
        #if game == game_id
        #    join()
    # new game
    resp = redirect('/game.html')
    #resp
    return resp
