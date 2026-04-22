import random
from train_card import TrainCard


class TrainDeck:
    def __init__(self):
        self.draw_pile = [
            TrainCard(color)
            for color in TrainCard.COLORS
            for _ in range(12)
        ] + [TrainCard("locomotive") for _ in range(14)]
        self.discard_pile = []
        self.face_up = []
        random.shuffle(self.draw_pile)
        self._deal_face_up()

    def _deal_face_up(self):
        self.face_up = [self.draw() for _ in range(5)]
        self._fix_locomotives()

    def get_face_up(self):
        return self.face_up

    def draw(self):
        if not self.draw_pile:
            self._reshuffle()
        return self.draw_pile.pop() if self.draw_pile else None

    def draw_face_up(self, index):
        if index < 0 or index >= len(self.face_up) or self.face_up[index] is None:
            return None
        card = self.face_up[index]
        self.face_up[index] = self.draw()
        self._fix_locomotives()
        return card

    def discard(self, cards):
        self.discard_pile.extend(c for c in cards if c is not None)

    def _reshuffle(self):
        if self.discard_pile:
            self.draw_pile = self.discard_pile[:]
            self.discard_pile.clear()
            random.shuffle(self.draw_pile)

    def _fix_locomotives(self):
        safety = 0
        while sum(1 for c in self.face_up if c and c.is_locomotive()) >= 3:
            safety += 1
            if safety > 10:
                break
            self.discard(self.face_up)
            self.face_up = [self.draw() for _ in range(5)]
            if all(card is None for card in self.face_up):
                break