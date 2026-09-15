import random
import unittest

from shut_the_box_strategy_comparison import (
    find_valid_moves,
    play_game,
    run_simulation,
    select_move,
)


class SimulationTests(unittest.TestCase):
    def test_find_valid_moves_returns_every_combination(self) -> None:
        moves = find_valid_moves(5, [1, 2, 3, 4])
        self.assertEqual(set(moves), {(1, 4), (2, 3)})

    def test_min_count_prefers_a_single_tile(self) -> None:
        moves = find_valid_moves(9, list(range(1, 10)))
        self.assertEqual(select_move(moves, "min_count", list(range(1, 10))), (9,))

    def test_unknown_strategy_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown strategy"):
            select_move([(1, 2)], "not-a-strategy", [1, 2])

    def test_game_score_stays_within_valid_bounds(self) -> None:
        score = play_game("preserve_7s", rng=random.Random(43))
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 45)

    def test_seeded_simulation_is_reproducible(self) -> None:
        first = run_simulation(
            sessions=10, games_per_session=5, seed=43, strategies=["min_count"]
        )
        second = run_simulation(
            sessions=10, games_per_session=5, seed=43, strategies=["min_count"]
        )
        self.assertEqual(first, second)

    def test_non_positive_run_size_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "must both be positive"):
            run_simulation(sessions=0)


if __name__ == "__main__":
    unittest.main()
