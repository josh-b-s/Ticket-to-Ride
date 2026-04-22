import random
from train_card import TrainCard


class TrainDeck:
    def __init__(self):
        self.draw_pile = []
        self.discard_pile = []
        self.face_up = []

        self._build_deck()
        self._deal_face_up()

    def _build_deck(self):
        # 12 of each color
        for color in TrainCard.COLORS:
            for _ in range(12):
                self.draw_pile.append(TrainCard(color))

        # 14 locomotives
        for _ in range(14):
            self.draw_pile.append(TrainCard("locomotive"))

        random.shuffle(self.draw_pile)

    def _deal_face_up(self):
        self.face_up = [self.draw() for _ in range(5)]
        self._fix_locomotives()

    def draw(self):
        if not self.draw_pile:
            self._reshuffle()

        if not self.draw_pile:
            return None

        return self.draw_pile.pop()

    def draw_face_up(self, index):
        card = self.face_up[index]
        self.face_up[index] = self.draw()
        self._fix_locomotives()
        return card

    def discard(self, cards):
        self.discard_pile.extend(cards)

    def _reshuffle(self):
        if not self.discard_pile:
            return
        self.draw_pile = self.discard_pile[:]
        self.discard_pile.clear()
        random.shuffle(self.draw_pile)

    def _fix_locomotives(self):
        while sum(1 for c in self.face_up if c and c.is_locomotive()) >= 3:
            self.discard(self.face_up)
            self.face_up = [self.draw() for _ in range(5)]