import collections


class Trigger:

    def __init__(self, event, action):
        self.event = event
        self.action = action

SUMMONED = 'summoned'


class Minion:

    def __init__(self, health: int, attack: int, keywords=None, triggers=None):
        self.health = health
        self.attack = attack
        self.keywords = keywords or []
        self.triggers = triggers or []


class WarPack(collections.UserList):
    pass


MurlocScout = Minion(health=1, attack=1)

MurlocTidehunter = Minion(
    health=2,
    attack=1,
    triggers=[
        Trigger(SUMMONED, None)
    ]
)

