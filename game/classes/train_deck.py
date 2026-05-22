import random

from game.classes.train_card import TrainCard

_FACE_UP_SIZE         = 5
_MAX_LOCO_FIX_ATTEMPTS = 10


class TrainDeck:
    def __init__(self) -> None:
        self.draw_pile: list[TrainCard] = (
            [TrainCard(c) for c in TrainCard.COLORS for _ in range(12)]
            + [TrainCard("locomotive") for _ in range(14)]
        )
        self.discard_pile: list[TrainCard] = []
        self.face_up: list[TrainCard | None] = []
        random.shuffle(self.draw_pile)
        self._deal_face_up()

    # ── Public ────────────────────────────────────────────────────────────────

    def get_face_up(self) -> list[TrainCard | None]:
        return self.face_up

    def draw(self) -> TrainCard | None:
        if not self.draw_pile:
            self._reshuffle()
        return self.draw_pile.pop() if self.draw_pile else None

    def draw_face_up(self, index: int) -> TrainCard | None:
        if not (0 <= index < len(self.face_up)) or self.face_up[index] is None:
            return None
        card               = self.face_up[index]
        self.face_up[index] = self.draw()
        self._fix_locomotives()
        return card

    def discard(self, cards: list[TrainCard | None]) -> None:
        self.discard_pile.extend(c for c in cards if c is not None)

    # ── Private ───────────────────────────────────────────────────────────────

    def _deal_face_up(self) -> None:
        self.face_up = [self.draw() for _ in range(_FACE_UP_SIZE)]
        self._fix_locomotives()

    def _reshuffle(self) -> None:
        if self.discard_pile:
            self.draw_pile   = self.discard_pile[:]
            self.discard_pile = []
            random.shuffle(self.draw_pile)

    def _fix_locomotives(self) -> None:
        """Redeal face-up cards if 3+ locomotives appear (per rules)."""
        for _ in range(_MAX_LOCO_FIX_ATTEMPTS):
            if sum(1 for c in self.face_up if c and c.is_locomotive()) < 3:
                break
            self.discard(self.face_up)
            self.face_up = []
            if not self.draw_pile and not self.discard_pile:
                self.face_up = [None] * _FACE_UP_SIZE
                break
            self.face_up = [self.draw() for _ in range(_FACE_UP_SIZE)]
            if all(c is None for c in self.face_up):
                break
