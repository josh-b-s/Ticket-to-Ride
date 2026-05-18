import random

from train_card import TrainCard

_FACE_UP_SIZE = 5
_MAX_LOCO_FIX_ATTEMPTS = 10


class TrainDeck:
    def __init__(self):
        self.draw_pile: list[TrainCard] = (
            [TrainCard(c) for c in TrainCard.COLORS for _ in range(12)]
            + [TrainCard("locomotive") for _ in range(14)]
        )
        self.discard_pile: list[TrainCard] = []
        self.face_up: list[TrainCard | None] = []
        random.shuffle(self.draw_pile)
        self._deal_face_up()

    # ------------------------------------------------------------------ public

    def get_face_up(self) -> list[TrainCard | None]:
        return self.face_up

    def draw(self) -> TrainCard | None:
        if not self.draw_pile:
            self._reshuffle()
        return self.draw_pile.pop() if self.draw_pile else None

    def draw_face_up(self, index: int) -> TrainCard | None:
        if not (0 <= index < len(self.face_up)) or self.face_up[index] is None:
            return None
        card = self.face_up[index]
        self.face_up[index] = self.draw()
        self._fix_locomotives()
        return card

    def discard(self, cards: list[TrainCard | None]) -> None:
        self.discard_pile.extend(c for c in cards if c is not None)

    # ----------------------------------------------------------------- private

    def _deal_face_up(self) -> None:
        self.face_up = [self.draw() for _ in range(_FACE_UP_SIZE)]
        self._fix_locomotives()

    def _reshuffle(self) -> None:
        if self.discard_pile:
            self.draw_pile = self.discard_pile[:]
            self.discard_pile.clear()
            random.shuffle(self.draw_pile)

    def _fix_locomotives(self) -> None:
        """
        Redeal face-up cards if 3+ locomotives appear (per rules).

        BUG FIX: added early exit when the combined draw + discard pile is
        exhausted so we don't loop _MAX_LOCO_FIX_ATTEMPTS times uselessly
        on a near-empty deck.
        """
        for _ in range(_MAX_LOCO_FIX_ATTEMPTS):
            loco_count = sum(1 for c in self.face_up if c and c.is_locomotive())
            if loco_count < 3:
                break

            # Return current face-up cards to discard before redrawing.
            self.discard(self.face_up)
            self.face_up = []

            # If there are no cards left at all, stop trying.
            if not self.draw_pile and not self.discard_pile:
                self.face_up = [None] * _FACE_UP_SIZE
                break

            self.face_up = [self.draw() for _ in range(_FACE_UP_SIZE)]

            # If every slot is empty the deck is exhausted; nothing to fix.
            if all(c is None for c in self.face_up):
                break