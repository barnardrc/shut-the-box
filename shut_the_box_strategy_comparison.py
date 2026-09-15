"""Compare deterministic move-selection strategies for Shut the Box."""

from __future__ import annotations

import argparse
import itertools
import random
import statistics
from collections.abc import Iterable, Sequence
from dataclasses import dataclass


STRATEGIES = (
    "largest_val",
    "lowest_range",
    "min_count",
    "composite1",
    "composite2",
    "preserve_7s",
    "composite2_with_7s",
    "composite2_with_7s_2nd",
    "composite2_with_7s_3rd",
)


@dataclass(frozen=True)
class SimulationResult:
    """Aggregate score for one strategy."""

    strategy: str
    average_session_total: float
    average_game_score: float


def get_roll(current_board: Sequence[int], rng: random.Random | None = None) -> int:
    """Roll one die when the remaining total is six or less, otherwise two."""

    generator = rng or random
    dice = 1 if sum(current_board) <= 6 else 2
    return sum(generator.randint(1, 6) for _ in range(dice))


def find_valid_moves(target_sum: int, available_nums: Sequence[int]) -> list[tuple[int, ...]]:
    """Return every combination of available tiles that sums to ``target_sum``."""

    return [
        combo
        for length in range(1, len(available_nums) + 1)
        for combo in itertools.combinations(available_nums, length)
        if sum(combo) == target_sum
    ]


def count_ways_to_make_target(board: Sequence[int], target: int) -> int:
    """Count unique combinations of up to four tiles that sum to ``target``."""

    return sum(
        sum(combo) == target
        for length in range(1, min(len(board) + 1, 5))
        for combo in itertools.combinations(board, length)
    )


def select_move(
    moves: Sequence[tuple[int, ...]], strategy_name: str, current_board: Sequence[int]
) -> tuple[int, ...] | None:
    """Choose a legal move using a named deterministic heuristic."""

    if not moves:
        return None
    if strategy_name not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {strategy_name}")

    if strategy_name == "largest_val":
        return max(moves, key=lambda move: (max(move), len(move)))
    if strategy_name == "lowest_range":
        return min(moves, key=lambda move: max(move) - min(move))
    if strategy_name == "min_count":
        return min(moves, key=len)
    if strategy_name == "composite1":
        return max(
            moves,
            key=lambda move: (max(move), -len(move), max(move) - min(move)),
        )
    if strategy_name == "composite2":
        return max(moves, key=lambda move: (-len(move), max(move) - min(move)))

    def score_move(move: tuple[int, ...]) -> tuple[int, int, int]:
        future_board = [tile for tile in current_board if tile not in move]
        return (
            count_ways_to_make_target(future_board, 7),
            -len(move),
            max(move) - min(move),
        )

    if strategy_name == "preserve_7s":
        return max(
            moves,
            key=lambda move: (
                count_ways_to_make_target(
                    [tile for tile in current_board if tile not in move], 7
                ),
                -len(move),
                max(move),
            ),
        )
    if strategy_name == "composite2_with_7s":
        return max(moves, key=score_move)
    if strategy_name == "composite2_with_7s_2nd":
        return max(
            moves,
            key=lambda move: (score_move(move)[1], score_move(move)[0], score_move(move)[2]),
        )
    return max(
        moves,
        key=lambda move: (score_move(move)[1], score_move(move)[2], score_move(move)[0]),
    )


def play_game(
    strategy_name: str,
    *,
    rng: random.Random | None = None,
    verbose: bool = False,
) -> int:
    """Play one game and return the sum of tiles left open (lower is better)."""

    board = list(range(1, 10))
    generator = rng or random.Random()

    while board:
        roll = get_roll(board, generator)
        moves = find_valid_moves(roll, board)
        if not moves:
            if verbose:
                print(f"Game over: rolled {roll}; remaining tiles: {board}")
            break

        chosen_move = select_move(moves, strategy_name, board)
        if verbose:
            print(f"Rolled {roll} | Board {board} | Chose {chosen_move}")
        for tile in chosen_move or ():
            board.remove(tile)

    return sum(board)


def run_simulation(
    *,
    sessions: int = 1_000,
    games_per_session: int = 10,
    seed: int | None = None,
    strategies: Iterable[str] = STRATEGIES,
) -> list[SimulationResult]:
    """Simulate each strategy and return comparable aggregate results."""

    if sessions < 1 or games_per_session < 1:
        raise ValueError("sessions and games_per_session must both be positive")

    results: list[SimulationResult] = []
    for index, strategy in enumerate(strategies):
        strategy_rng = random.Random(None if seed is None else seed + index)
        session_totals = [
            sum(
                play_game(strategy, rng=strategy_rng)
                for _ in range(games_per_session)
            )
            for _ in range(sessions)
        ]
        average_session = statistics.fmean(session_totals)
        results.append(
            SimulationResult(
                strategy=strategy,
                average_session_total=average_session,
                average_game_score=average_session / games_per_session,
            )
        )
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare Shut the Box move-selection heuristics with Monte Carlo simulation."
    )
    parser.add_argument("--sessions", type=int, default=1_000)
    parser.add_argument("--games-per-session", type=int, default=10)
    parser.add_argument("--seed", type=int, default=None)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    results = run_simulation(
        sessions=args.sessions,
        games_per_session=args.games_per_session,
        seed=args.seed,
    )
    print(f"{'STRATEGY':<28} | {'AVG SESSION':>12} | {'AVG GAME':>10}")
    print("-" * 59)
    for result in sorted(results, key=lambda item: item.average_game_score):
        print(
            f"{result.strategy:<28} | "
            f"{result.average_session_total:>12.2f} | "
            f"{result.average_game_score:>10.2f}"
        )


if __name__ == "__main__":
    main()
