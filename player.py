from trueskill import Rating, rate, rate_1vs1, quality_1vs1


class Player():

    def __init__(self, name):
        self.name = name
        self.terran = Rating()
        self.protoss = Rating()
        self.zerg = Rating()
