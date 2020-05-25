from trueskill import Rating, rate, rate_1vs1, quality_1vs1


class Stats():
    def __init__(self):
        self.current_trueskill = Rating()
        self.history = []
        self.games_played = 0
        self.games_won = 0
        self.games_lost = 0
