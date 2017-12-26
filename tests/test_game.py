import pytest


def setup_module(module):
    global game
    from mafiservo import game


@pytest.fixture()
def civil():
    return game.Player('civil', 1)


@pytest.fixture()
def mafia():
    return game.Player('mafia', 1)


@pytest.fixture()
def doctor():
    return game.Player('doctor', 1)


def test_player_unique_id(civil):
    assert civil != game.Player('civil', 2).uuid


def test_player_die(civil):
    civil.die()


def test_player_die_twice(civil):
    with pytest.raises(game.GameError):
        civil.die()
        civil.die()


def test_heal_normal_player(civil):
    civil.heal()
    civil.heal()


def test_heal_doctor_once(doctor):
    doctor.heal()


def test_heal_doctor_twice(doctor):
    doctor.heal()
    with pytest.raises(game.GameError):
        doctor.heal()


@pytest.mark.parametrize('action', ['heal', 'take', 'check', 'mafia_kill'])
def test_no_actions_on_dead(civil, action):
    civil.die()
    with pytest.raises(game.GameError):
        getattr(civil, action)()


@pytest.mark.parametrize('role, action', [
    ['mafia', 'mafia_kill'],
    ['girl', 'take'],
    ['sheriff', 'check'],
])
def test_no_action_on_self(role, action):
    player = game.Player(role, 1)
    with pytest.raises(game.GameError):
        getattr(player, action)()


@pytest.mark.parametrize('total, mafia, sheriff, doctor, girl', [
    [10, 3, True, True, False],
    [8, 2, True, False, False],
    [4, 1, True, True, True],
    [3, 1, False, False, False]
])
def test_game_normal_set(total, mafia, sheriff, doctor, girl):
    game.Game(total, mafia, sheriff, doctor, girl)


@pytest.mark.parametrize('total, mafia, sheriff, doctor, girl', [
    [0, 0, False, False, False],
    [1, 2, False, False, False],
    [3, 1, True, True, True],
])
def test_game_incorrect_set(total, mafia, sheriff, doctor, girl):
    with pytest.raises(game.BadSettings):
        game.Game(total, mafia, sheriff, doctor, girl)


@pytest.mark.parametrize('civil_count, mafia_count, result', [
    [10, 3, None],
])
def test_check_game_status(civil_count, mafia_count, result):
    g = game.Game(10, 3)
    g.players = {}
    for i in range(civil_count):
        g.players[i] = game.Player('civil', i)
    for j in range(mafia_count):
        g.players[civil_count + j] = game.Player('mafia', civil_count + j)
    if result:
        with pytest.raises(result):
            g.night_results()
    else:
        g.night_results()
