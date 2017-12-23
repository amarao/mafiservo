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
