import random


class Availability:
    """Per-client availability with return (no torch, so it can be tested without a GPU).

    Every available client drops with probability `drop` per round and stays out for
    L ~ U{1, ..., rounds} rounds (the dropping round included). The round after an absence
    is a return round: the client is available and is not drawn, so two absences are never
    adjacent and nobody is out for more than `rounds` consecutive rounds.
    """

    def __init__(self, n, drop, rounds, seed):
        if not 0 <= drop < 1:
            raise ValueError("drop must be in [0, 1), got {}".format(drop))
        if rounds < 1:
            raise ValueError("rounds must be >= 1, got {}".format(rounds))
        self.n = n
        self.drop = drop
        self.rounds = rounds
        self.rng = random.Random("drop-{}".format(seed)) # own generator, the global one is not consumed
        self.down_left = [0] * n # rounds of absence left after the current one
        self.grace = [False] * n # the current round is the return round

    def step(self):
        """Advance one round (call it once per round, the first included). Returns up[c] for each client."""
        up = [True] * self.n
        if self.drop == 0:
            return up
        for c in range(self.n):
            if self.down_left[c] > 0:
                up[c] = False
                self.down_left[c] -= 1
                self.grace[c] = self.down_left[c] == 0
            elif self.grace[c]:
                self.grace[c] = False
            elif self.rng.random() < self.drop:
                length = self.rng.randint(1, self.rounds)
                up[c] = False
                self.down_left[c] = length - 1
                self.grace[c] = length == 1
        return up
