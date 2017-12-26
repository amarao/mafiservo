import random
import uuid


class GameError(Exception):
    pass


class BadSettings(GameError):
    pass


class GameEnd(BaseException):
    '''
        not a normal Exception, just a signal that game has
        ended
    '''
    pass


class MafiaWon(GameEnd):
    pass


class CivilsWon(GameEnd):
    pass


class Player(object):
    def __init__(self, role, name):
        self.role = role
        self.id = str(uuid.uuid4())
        self.name = name
        self.is_alive = True
        self.self_healed = False
        self.uuid = str(uuid.uuid4())

    def die(self):
        if not self.is_alive:
            raise GameError(
                "player %s was killed twice!" % self.name
            )
        self.is_alive = False

    def heal(self):
        if self.role == 'doctor' and self.self_healed:
            raise GameError("Doctor should heal itself only once")
        if not self.is_alive:
            raise GameError("Doctor shouldn't heal dead")
        self.self_healed = True

    def take(self):
        if self.role == 'girl':
            raise GameError("Girl shouldn't take herself")
        if not self.is_alive:
            raise GameError("Girl shouldn't enterntain dead")

    def check(self):
        if self.role == 'sheriff':
            raise GameError("Sheriff couldn't check itself")
        if not self.is_alive:
            raise GameError("Sheriff couldn't check dead")

    def mafia_kill(self):
        if self.role == 'mafia':
            raise GameError("Mafia can't kill own kind")
        if not self.is_alive:
            raise GameError("Mafia can't kill dead")


class Game(object):
    def __init__(
        self,
        total_players,
        mafia_num,
        is_sheriff=True,
        is_doctor=True,
        is_girl=False
    ):
        if total_players < (
            mafia_num +
            int(is_sheriff) +
            int(is_doctor) +
            int(is_girl)
        ):
            raise BadSettings("Not enought players! No civils!")
        if mafia_num * 2 >= total_players:
            raise BadSettings("Too many mafia!")
        self.total_players = total_players
        self.mafia_num = mafia_num
        self.is_sheriff = is_sheriff
        self.is_doctor = is_doctor
        self.is_girl = is_girl
        self.players = {}
        self._init_players()
        self.doctor_vote = None
        self.mafia_vote = None
        self.girl_vote = None

    def _init_players(self):
        roles = ['mafia'] * self.mafia_num
        if self.is_doctor:
            roles += ['doctor']
        if self.is_sheriff:
            roles += ['sheriff']
        if self.is_girl:
            roles += ['girl']
        roles += ['civil'] * (self.total_players - len(roles))
        random.shuffle(roles)
        names = list(range(1, self.total_players + 1))
        random.shuffle(names)
        for name, role in zip(names, roles):
            self.players[name] = Player(role, name)

    def day_kills(self, killed_players):
        for player_name in killed_players:
            self.player[player_name].die()
        self.check_game_status()

    def mafia_vote(self, vote):
        self.player[vote].mafia_kill()
        self.mafia_vote = vote

    def sheriff_check(self, vote):
        self.player[vote].check()
        if self.player[vote].role == 'mafia':
            return 'mafia'
        else:
            return 'civil'

    def doctor_vote(self, vote):
        self.player[vote].heal()
        self.doctor_vote = vote

    def girl_vote(self, vote):
        self.player[vote].take()
        self.girl_vote = vote

    def night_results(self):
        if self.mafia_vote == self.doctor_vote:
            return []
        if self.mafia_vote == self.girl_vote:
            return []
        if self.player[self.mafia_vote].role == 'girl':
            self.player[self.mafia_vote].die()
            self.player[self.girl_vote].die()
            return [self.mafia_vote, self.girl_vote]
        self.player[self.mafia_vote].die()
        return [self.mafia_vote]

    def morning(self):
        results = self.night_results()
        self.mafia_vote = None
        self.doctor_vote = None
        self.girl_vote = None
        self.check_game_status()
        return results

    def check_game_status(self):
        mafia_count = 0
        civil_count = 0
        for player in self.players:
            if player.is_alive and player.role == 'mafia':
                mafia_count += 1
            if player.is_alive and player.role != 'mafia':
                civil_count += 1
        if mafia_count >= civil_count:
            raise MafiaWon()
        if mafia_count == 0:
            raise CivilsWon()
