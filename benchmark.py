import os
import json
import time
import argparse
import itertools
from collections import defaultdict
from typing import Dict, Any, Tuple, List

from algorithms import registry
from game import Game  # Game.__init__(self, k, x, lower, bound)

MOVES_DIR = "saved_runs_moves"
STATS_DIR = "saved_games"


def play_game(
    game: Game, algo1: str, algo2: str, record_moves: bool = False
) -> Tuple[int, float, float, List[int]]:
    """
    Simulates a single game between algo1 (player1) and algo2 (player2).
    Returns (winner, time1, time2, moves_log).
    """
    moves_log: List[int] = []
    t1 = t2 = 0.0

    strat1 = registry.get(algo1.lower(), registry["random"])
    strat2 = registry.get(algo2.lower(), registry["random"])

    while not game.game_over:
        if game.player1_turn:
            start = time.time()
            move = strat1(
                list(game.available_numbers),
                game.player1_moves,
                game.player2_moves,
                game.k,
            )
            t1 += time.time() - start
        else:
            start = time.time()
            move = strat2(
                list(game.available_numbers),
                game.player2_moves,
                game.player1_moves,
                game.k,
            )
            t2 += time.time() - start

        game.make_move(move)
        if record_moves:
            moves_log.append(move)

    winner_code = game.winner or 0
    return winner_code, t1, t2, moves_log


def run_tournament(
    settings: Dict[str, Any], num_games: int = 10, save_moves: bool = False
) -> Dict[str, Any]:
    """
    Runs every ordered pairing of registered algorithms num_games times.
    Saves per-game move logs if requested, and writes aggregate stats.
    """
    os.makedirs(MOVES_DIR, exist_ok=True)
    os.makedirs(STATS_DIR, exist_ok=True)

    algos = list(registry.keys())
    total_matches = len(algos) * (len(algos) - 1) * num_games
    print(
        f"Running experiments: {len(algos)} algorithms, {num_games} games each pairing ({total_matches} total games)..."
    )

    results = {
        "wins": defaultdict(int),
        "losses": defaultdict(int),
        "draws": defaultdict(int),
        "points": defaultdict(float),
        "execution_time": defaultdict(float),
        "matchups": {
            a: {b: {"wins": 0, "losses": 0, "draws": 0} for b in algos} for a in algos
        },
        "total_games": 0,
    }

    k = settings["k"]
    x = settings["x"]
    lower = settings["lower"]
    bound = settings["bound"]

    for a1, a2 in itertools.permutations(algos, 2):
        for i in range(1, num_games + 1):
            game = Game(k, x, lower, bound)
            winner, t1, t2, moves = play_game(game, a1, a2, record_moves=save_moves)

            # Tally results
            if winner == 1:
                results["wins"][a1] += 1
                results["losses"][a2] += 1
                results["points"][a1] += 1
                results["matchups"][a1][a2]["wins"] += 1
            elif winner == 2:
                results["wins"][a2] += 1
                results["losses"][a1] += 1
                results["points"][a2] += 1
                results["matchups"][a2][a1]["wins"] += 1
            else:
                results["draws"][a1] += 1
                results["draws"][a2] += 1
                results["points"][a1] += 0.5
                results["points"][a2] += 0.5
                results["matchups"][a1][a2]["draws"] += 1

            results["execution_time"][a1] += t1
            results["execution_time"][a2] += t2
            results["total_games"] += 1

            # Save move log if requested, filename now includes the game ID
            if save_moves:
                fname = f"{a1}_vs_{a2}_game_{i}.json"
                with open(os.path.join(MOVES_DIR, fname), "w") as f:
                    json.dump(
                        {
                            "settings": settings,
                            "grid": game.X,
                            "first_player": a1,
                            "second_player": a2,
                            "game_id": i,
                            "moves": moves,
                        },
                        f,
                        indent=2,
                    )

    # Write out aggregate statistics
    timestamp = int(time.time())
    stats_file = os.path.join(STATS_DIR, f"tournament_{timestamp}.json")
    with open(stats_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Experiments completed. Results saved to {stats_file}")
    ranking = sorted(results["points"].items(), key=lambda x: -x[1])
    for algo, pts in ranking:
        print(f"{algo}: {pts} points")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run round-robin tournament of all AI strategies."
    )
    parser.add_argument(
        "--config",
        required=False,
        help=(
            "Path to JSON config (example format):\n"
            "{\n"
            '  "k": 4,\n'
            '  "x": 30,\n'
            '  "lower": 1,\n'
            '  "bound": 100,\n'
            '  "num_games": 10,\n'
            '  "save_moves": true\n'
            "}"
        ),
    )
    args = parser.parse_args()

    # Default config
    cfg = {
        "k": 4,
        "x": 30,
        "lower": 1,
        "bound": 100,
        "num_games": 10,
        "save_moves": False,
    }
    if args.config:
        with open(args.config) as f:
            cfg.update(json.load(f))

    run_tournament(
        settings={
            "k": cfg["k"],
            "x": cfg["x"],
            "lower": cfg["lower"],
            "bound": cfg["bound"],
        },
        num_games=cfg["num_games"],
        save_moves=cfg["save_moves"],
    )
