"""
tests/test_core.py

Unit tests for Sprint 3 core game logic.
Run from the project root:
    python -m pytest game/tests/ -v
or:
    python -m unittest discover -s game/tests -v
"""
import unittest
from game.classes.route import Route, RouteColor, CardPlan
from game.classes.player import Player
from game.services.move_validator import MoveValidator, ValidationResult
from game.classes.train_card import TrainCard


# ─────────────────────────────────────────────────────────────
# Route.compute_card_slots — standard routes
# ─────────────────────────────────────────────────────────────

class TestComputeCardSlotsStandard(unittest.TestCase):

    def setUp(self):
        self.route = Route("A", "B", 3, RouteColor.BLUE)

    def test_exact_colour_cards(self):
        """3 colour cards, 0 locos — should succeed."""
        plan = self.route.compute_card_slots(3, 0)
        self.assertIsNotNone(plan)
        self.assertEqual(plan.color_to_use, 3)
        self.assertEqual(plan.total_locos, 0)

    def test_colour_plus_loco_wildcard(self):
        """2 colour + 1 loco filling the gap — should succeed."""
        plan = self.route.compute_card_slots(2, 1)
        self.assertIsNotNone(plan)
        self.assertEqual(plan.color_to_use, 2)
        self.assertEqual(plan.total_locos, 1)

    def test_all_locos(self):
        """3 locos, 0 colour — locos act as full wilds."""
        plan = self.route.compute_card_slots(0, 3)
        self.assertIsNotNone(plan)
        self.assertEqual(plan.total_locos, 3)

    def test_insufficient_cards_returns_none(self):
        """1 colour + 1 loco for a length-3 route — should fail."""
        plan = self.route.compute_card_slots(1, 1)
        self.assertIsNone(plan)

    def test_zero_cards_returns_none(self):
        plan = self.route.compute_card_slots(0, 0)
        self.assertIsNone(plan)

    def test_exact_boundary(self):
        """Exactly enough — length-1 route with 1 colour card."""
        route = Route("A", "B", 1, RouteColor.GREEN)
        plan = route.compute_card_slots(1, 0)
        self.assertIsNotNone(plan)

    def test_one_short_returns_none(self):
        """One card short of requirement."""
        plan = self.route.compute_card_slots(2, 0)
        self.assertIsNone(plan)


# ─────────────────────────────────────────────────────────────
# Route.compute_card_slots — ferry routes
# ─────────────────────────────────────────────────────────────

class TestComputeCardSlotsFerry(unittest.TestCase):

    def setUp(self):
        # Ferry route: length 3, requires 1 locomotive for the ferry symbol
        self.ferry = Route("A", "B", 3, RouteColor.BLUE, ferry_locos=1)

    def test_ferry_sufficient_loco_and_colour(self):
        """1 loco + 2 colour cards for a 3-length, 1-ferry route."""
        plan = self.ferry.compute_card_slots(2, 1)
        self.assertIsNotNone(plan)
        self.assertEqual(plan.locos_for_ferry, 1)
        self.assertEqual(plan.color_to_use, 2)

    def test_ferry_three_for_one_substitution(self):
        """0 locos — each missing loco costs 3 colour cards.
        ferry_locos=1, so need 3 extra colour cards + 2 normal = 5 colour total."""
        plan = self.ferry.compute_card_slots(5, 0)
        self.assertIsNotNone(plan)

    def test_ferry_insufficient_locos_insufficient_colour(self):
        """Not enough locos and not enough colour to substitute."""
        plan = self.ferry.compute_card_slots(1, 0)
        self.assertIsNone(plan)

    def test_ferry_two_locos_required(self):
        """Route with 2 ferry symbols: length 4, ferry_locos=2."""
        ferry2 = Route("A", "B", 4, RouteColor.ORANGE, ferry_locos=2)
        # 2 locos + 2 colour cards covers all slots
        plan = ferry2.compute_card_slots(2, 2)
        self.assertIsNotNone(plan)
        self.assertEqual(plan.locos_for_ferry, 2)

    def test_ferry_extra_locos_act_as_wilds(self):
        """Extra locos beyond ferry requirement fill colour slots."""
        plan = self.ferry.compute_card_slots(0, 3)
        self.assertIsNotNone(plan)

    def test_ferry_returns_none_when_one_colour_short(self):
        """4 colour (need 5 for 3-for-1) + 0 locos — should fail."""
        plan = self.ferry.compute_card_slots(4, 0)
        self.assertIsNone(plan)


# ─────────────────────────────────────────────────────────────
# Route predicates
# ─────────────────────────────────────────────────────────────

class TestRoutePredicates(unittest.TestCase):

    def test_is_ferry_true(self):
        route = Route("A", "B", 2, RouteColor.BLUE, ferry_locos=1)
        self.assertTrue(route.is_ferry())

    def test_is_ferry_false(self):
        route = Route("A", "B", 2, RouteColor.BLUE)
        self.assertFalse(route.is_ferry())

    def test_is_gray_true(self):
        route = Route("A", "B", 2, RouteColor.GRAY)
        self.assertTrue(route.is_gray())

    def test_is_gray_false(self):
        route = Route("A", "B", 2, RouteColor.BLUE)
        self.assertFalse(route.is_gray())

    def test_is_claimed_false_initially(self):
        route = Route("A", "B", 2, RouteColor.BLUE)
        self.assertFalse(route.is_claimed())

    def test_is_claimed_true_after_owner_set(self):
        route = Route("A", "B", 2, RouteColor.BLUE)
        route.owner_player = Player("Alice")
        self.assertTrue(route.is_claimed())

    def test_connects_correct(self):
        route = Route("London", "Paris", 3, RouteColor.GREEN)
        self.assertTrue(route.connects("London", "Paris"))
        self.assertTrue(route.connects("Paris", "London"))

    def test_connects_wrong_cities(self):
        route = Route("London", "Paris", 3, RouteColor.GREEN)
        self.assertFalse(route.connects("London", "Berlin"))


# ─────────────────────────────────────────────────────────────
# MoveValidator
# ─────────────────────────────────────────────────────────────

class TestMoveValidator(unittest.TestCase):

    def setUp(self):
        self.validator = MoveValidator()
        self.player = Player("Alice")
        self.player.trains = 17

    def _make_cards(self, colour: str, count: int) -> list:
        return [TrainCard(colour) for _ in range(count)]

    def _make_locos(self, count: int) -> list:
        return [TrainCard("locomotive") for _ in range(count)]

    def test_valid_claim_standard_route(self):
        route = Route("A", "B", 2, RouteColor.BLUE)
        self.player.train_cards = self._make_cards("blue", 2)
        result = self.validator.validate_claim(
            self.player, route, None, [route], 4
        )
        self.assertTrue(result.ok)

    def test_already_claimed_route(self):
        route = Route("A", "B", 2, RouteColor.BLUE)
        route.owner_player = Player("Bob")
        result = self.validator.validate_claim(
            self.player, route, None, [route], 4
        )
        self.assertFalse(result.ok)
        self.assertIn("already claimed", result.reason.lower())

    def test_not_enough_trains(self):
        route = Route("A", "B", 5, RouteColor.BLUE)
        self.player.trains = 2
        self.player.train_cards = self._make_cards("blue", 5)
        result = self.validator.validate_claim(
            self.player, route, None, [route], 4
        )
        self.assertFalse(result.ok)
        self.assertIn("train", result.reason.lower())

    def test_not_enough_cards(self):
        route = Route("A", "B", 3, RouteColor.GREEN)
        self.player.train_cards = self._make_cards("green", 1)
        result = self.validator.validate_claim(
            self.player, route, None, [route], 4
        )
        self.assertFalse(result.ok)

    def test_hint_populated_on_failure(self):
        """Detailed illegal move feedback: hint must be non-empty on failure."""
        route = Route("A", "B", 3, RouteColor.GREEN)
        self.player.train_cards = self._make_cards("green", 1)
        result = self.validator.validate_claim(
            self.player, route, None, [route], 4
        )
        self.assertFalse(result.ok)
        self.assertGreater(len(result.hint), 0)

    def test_gray_route_no_colour_selected(self):
        route = Route("A", "B", 2, RouteColor.GRAY)
        self.player.train_cards = self._make_cards("blue", 2)
        result = self.validator.validate_claim(
            self.player, route, None, [route], 4
        )
        self.assertFalse(result.ok)

    def test_gray_route_with_colour_selected(self):
        route = Route("A", "B", 2, RouteColor.GRAY)
        self.player.train_cards = self._make_cards("blue", 2)
        result = self.validator.validate_claim(
            self.player, route, "blue", [route], 4
        )
        self.assertTrue(result.ok)

    def test_ferry_route_insufficient_locos_hint_mentions_substitution(self):
        """Ferry failure hint should explain the 3-for-1 substitution rule."""
        ferry = Route("A", "B", 3, RouteColor.BLUE, ferry_locos=1)
        self.player.train_cards = self._make_cards("blue", 1)  # not enough
        result = self.validator.validate_claim(
            self.player, ferry, None, [ferry], 4
        )
        self.assertFalse(result.ok)
        # Hint should mention substitution (3 cards replace 1 loco)
        self.assertTrue(
            "3" in result.hint or "replace" in result.hint.lower()
        )

    def test_parallel_route_blocked_two_player(self):
        """With 2 players, parallel routes are blocked once one is claimed."""
        route1 = Route("A", "B", 2, RouteColor.BLUE)
        route2 = Route("A", "B", 2, RouteColor.PINK)
        route1.owner_player = Player("Bob")
        self.player.train_cards = self._make_cards("pink", 2)
        result = self.validator.validate_claim(
            self.player, route2, None, [route1, route2], 2
        )
        self.assertFalse(result.ok)

    def test_parallel_route_allowed_four_player(self):
        """With 4 players, both parallel routes can be claimed."""
        route1 = Route("A", "B", 2, RouteColor.BLUE)
        route2 = Route("A", "B", 2, RouteColor.PINK)
        route1.owner_player = Player("Bob")
        self.player.train_cards = self._make_cards("pink", 2)
        result = self.validator.validate_claim(
            self.player, route2, None, [route1, route2], 4
        )
        self.assertTrue(result.ok)


# ─────────────────────────────────────────────────────────────
# ValidationResult dataclass
# ─────────────────────────────────────────────────────────────

class TestValidationResult(unittest.TestCase):

    def test_ok_result(self):
        r = ValidationResult(ok=True, reason="Claimed.", hint="")
        self.assertTrue(r.ok)

    def test_fail_result_has_reason(self):
        r = ValidationResult(ok=False, reason="Not enough cards.", hint="Need 3 blue.")
        self.assertFalse(r.ok)
        self.assertEqual(r.reason, "Not enough cards.")
        self.assertEqual(r.hint, "Need 3 blue.")


if __name__ == "__main__":
    unittest.main()