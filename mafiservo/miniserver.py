from flask import Flask
from flask import render_template, request, redirect, abort


MAFIA = []
MAFIA_COUNT = 3
MAFIA_KILL = None
DOCTOR_HEAL = None
app = Flask('mafiservo')


def get_kill():
    if MAFIA_KILL and MAFIA_KILL != DOCTOR_HEAL:
        return "Player %s" % str(MAFIA_KILL)
    return "No one"


@app.route('/')
def menu():
    return render_template("index.html")


@app.route('/last_kill')
def last_kill():
    if len(MAFIA) != MAFIA_COUNT:
        return render_template(
            "fail.html",
            message="Not all mafia were registered"
        )
    return render_template("status.html", player=get_kill())


@app.route('/mafia_register', methods=['POST'])
def mafia_register():
    global MAFIA
    if len(MAFIA) == MAFIA_COUNT:
        return render_template(
            "fail.html",
            message="All mafia are alredy registered"
        )
    player = request.form.get('player', None)
    if not player:
        return render_template(
            "fail.html", message="No player ID was supplied")
    if player in MAFIA:
        return render_template(
            "fail.html",
            message="Player %s is already registered" % player
        )
    MAFIA.append(request.form['player'])
    print("Mafia registered" + str(type(player)))
    return render_template(
        "success.html",
        player=player,
        action="registration"
    )


@app.route('/mafia_kill', methods=['POST'])
def mafia_kill():
    global MAFIA
    global MAFIA_KILL
    global DOCTOR_HEAL
    if len(MAFIA) != MAFIA_COUNT:
        return render_template(
            "fail.html",
            message="Not all mafia were registered"
        )
    player = request.form.get('player', None)
    if not player:
        return render_template(
            "fail.html", message="No player ID was supplied")
    MAFIA_KILL = player
    DOCTOR_HEAL = None
    return render_template(
        "success.html",
        player=player,
        action="assasination"
    )


@app.route('/doctor_heal', methods=['POST'])
def doctor_heal():
    global MAFIA
    global DOCTOR_HEAL
    if len(MAFIA) != MAFIA_COUNT:
        return render_template(
            "fail.html",
            message="Not all mafia were registered"
        )
    player = request.form.get('player', None)
    if not player:
        return render_template(
            "fail.html", message="No player ID was supplied")
    DOCTOR_HEAL = player
    print("Doctor healed")
    return render_template(
        "success.html",
        player=player,
        action="healing"
    )


@app.route('/sheriff_check', methods=['POST'])
def sheriff_check():
    global MAFIA
    if len(MAFIA) != MAFIA_COUNT:
        return render_template(
            "fail.html",
            message="Not all mafia were registered"
        )
    player = request.form.get('player', None)
    if not player:
        return render_template(
            "fail.html", message="No player ID was supplied")
    print("Sheriff checked")
    return render_template(
        "check_result.html",
        player=player,
        result=(player in MAFIA)
    )
