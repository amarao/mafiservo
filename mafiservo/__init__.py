from flask import Flask
from flask import render_template, request
import platform
import subprocess
import os
import time
import atexit


MAFIA = []
MAFIA_COUNT = 3
MAFIA_KILL = None
DOCTOR_HEAL = None
SHERIFF_MAY_CHECK = False
SOUND = None
app = Flask('mafiservo')


DEVNULL = os.open('/dev/null', os.O_RDWR)
PRIVATE_LOG = []


if platform.system() == 'Linux':
    PLAYER = 'mplayer'
elif platform.system() == 'Darwin':
    PLAYER = 'afpaly'
else:
    raise Exception("Unsupported OS: %s" % platform.system())


def bilogger(public, private):
    global PRIVATE_LOG
    PRIVATE_LOG.append("%s [%s] %s" % (
        time.strftime('%H:%M:%S'), request.remote_addr, private
    ))
    if public:
        print(public)


def dump_log():
    print("Post-game log:\n\n")
    for line in PRIVATE_LOG:
        print(line)
    print("\nEND")


atexit.register(dump_log)


class Config:
    mafia_count = 3
    is_doctor = True
    delay_before_sound = 3
    new_mafia = 'sounds/new_mafia.mp3'
    mafia_kill = 'sounds/shoot.mp3'
    sheriff = 'sounds/check.mp3'
    morning = 'sounds/morning.mp3'
    status = 'sounds/status.mp3'


def get_kill():
    global MAFIA_KILL
    global DOCTOR_HEAL
    if MAFIA_KILL and MAFIA_KILL != DOCTOR_HEAL:
        return "Player %s" % str(MAFIA_KILL)
    return "No one"


def play(sound, delay):
    global Config
    global PLAYER
    global DEVNULL
    bilogger(private="Playing sound %s" % SOUND, public=None)
    cmdline = 'sleep %s; %s %s' % (delay, PLAYER, sound)
    subprocess.Popen(
        cmdline, shell=True, stdout=DEVNULL, stdin=DEVNULL, stderr=DEVNULL)


@app.route('/')
def menu():
    global SOUND
    global request
    if SOUND:
        play(SOUND, Config.delay_before_sound)
    bilogger(
        public=None,
        private="Start page requested"
    )
    SOUND = None
    return render_template(
        "index.html", mafia=Config.mafia_count, doctor=Config.is_doctor)


@app.route('/last_kill')
def last_kill():
    global Config
    global MAFIA
    if len(MAFIA) != Config.mafia_count:
        return render_template(
            "fail.html",
            message="Not all mafia were registered"
        )
    play(Config.status, 0)
    message = "Status requested: %s was killed" % get_kill()
    bilogger(
        public=message,
        private=message
    )
    return render_template("status.html", player=get_kill())


@app.route('/mafia_register', methods=['POST'])
def mafia_register():
    global MAFIA
    global Config
    global SOUND
    if len(MAFIA) == Config.mafia_count:
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
    bilogger(
        public="Mafia member registered (%s of %s)" % (len(MAFIA), Config.mafia_count),
        private="Player %s is registered as mafia" % player
    )
    if len(MAFIA) == Config.mafia_count:
        SOUND = Config.new_mafia
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
    global SHERIFF_MAY_CHECK
    global Config
    global SOUND
    if len(MAFIA) != Config.mafia_count:
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
    SHERIFF_MAY_CHECK = True
    SOUND = Config.mafia_kill
    bilogger(
        public="Mafia selected a player",
        private="Mafia selected player %s" % player
    )
    return render_template(
        "success.html",
        player=player,
        action="assasination"
    )


@app.route('/doctor_heal', methods=['POST'])
def doctor_heal():
    global MAFIA
    global DOCTOR_HEAL
    global Config
    global SOUND
    if len(MAFIA) != Config.mafia_count:
        return render_template(
            "fail.html",
            message="Not all mafia were registered"
        )
    if not Config.is_doctor:
        return render_template(
            "fail.html",
            message="There is no doctor in this game"
        )
    player = request.form.get('player', None)
    if not player:
        return render_template(
            "fail.html", message="No player ID was supplied")
    DOCTOR_HEAL = player
    SOUND = Config.morning
    bilogger(
        public=None,
        private="Doctor healed player %s" % player
    )
    return render_template(
        "success.html",
        player=player,
        action="healing"
    )


@app.route('/sheriff_check', methods=['POST'])
def sheriff_check():
    global MAFIA
    global SHERIFF_MAY_CHECK
    global Config
    global SOUND
    if len(MAFIA) != Config.mafia_count:
        return render_template(
            "fail.html",
            message="Not all mafia were registered"
        )
    player = request.form.get('player', None)
    if not player:
        return render_template(
            "fail.html", message="No player ID was supplied")
    if not SHERIFF_MAY_CHECK:
        return render_template(
            "fail.html",
            message="You are not allowed to do second check in row (mafia kill required)."
        )
    SHERIFF_MAY_CHECK = False
    if Config.is_doctor:
        SOUND = Config.sheriff
    else:
        SOUND = Config.morning
    result = (player in MAFIA)
    bilogger(
        public=None,
        private="Sheriff checked player %s (%s)" % (player, result)
    )
    return render_template(
        "check_result.html",
        player=player,
        result=result
    )
