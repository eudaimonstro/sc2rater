from stats import Stats


class Player():

    def __init__(self, name):
        self.name = name
        self.terran = Stats()
        self.protoss = Stats()
        self.zerg = Stats()
