from flask import Flask
from flask import render_template
from flask import request

app = Flask('mafiservo')


@app.route('/')
def menu():
    return render_template("index.html")


@app.route('/game.html', methods=['POST'])
def game():
    import pdb
    pdb.set_trace()
    return request.form["players"]
