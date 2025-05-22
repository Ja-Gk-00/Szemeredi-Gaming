from typing import List
from . import register_algorithm
import random
import statistics
from itertools import combinations
from utils import find_all_arithmetic_progressions
from algorithms.MCTSNode import MCTSNode


@register_algorithm("random")
def choose_move(
    available_moves: List[int],
    current_held: List[int],
    opponent_held: List[int],
    k: int,
) -> int:
    if not available_moves:
        return -1
    return random.choice(available_moves)


@register_algorithm("heuristic")
def choose_move(
    available_moves: List[int],
    current_held: List[int],
    opponent_held: List[int],
    k: int,
) -> int:
    if not available_moves:
        return -1
    median_val: float = statistics.median(available_moves)
    best_score: float = -float("inf")
    best_move: int = available_moves[0]
    for num in available_moves:
        score: float = -abs(num - median_val)
        if current_held:
            score -= min(abs(num - x) for x in current_held)
        if score > best_score:
            best_score = score
            best_move = num
    return best_move


@register_algorithm("min")
def choose_move(
    available_moves: List[int],
    current_held: List[int],
    opponent_held: List[int],
    k: int,
) -> int:
    if not available_moves:
        return -1
    best_move = min(available_moves)
    return best_move


@register_algorithm("heuristic_fast")
def choose_move(
    available_moves: List[int],
    current_held: List[int],
    opponent_held: List[int],
    k: int,
) -> int:
    if not available_moves:
        return -1

    def is_ap(seq: List[int]) -> bool:
        seq = sorted(seq)
        d = seq[1] - seq[0]
        for i in range(1, len(seq)):
            if seq[i] - seq[i - 1] != d:
                return False
        return True

    for move in available_moves:
        for subset in combinations(current_held + [move], k):
            if is_ap(list(subset)):
                return move

    for move in available_moves:
        for subset in combinations(opponent_held + [move], k):
            if is_ap(list(subset)):
                return move

    def ap_potential(num: int, all_nums: List[int]) -> int:
        count = 0
        for x in all_nums:
            if x == num:
                continue
            d = abs(num - x)
            third = num + d if num > x else num - d
            if third in all_nums:
                count += 1
        return count

    best_score = -1
    best_move = available_moves[0]
    for move in available_moves:
        score = ap_potential(move, available_moves + current_held)
        if score > best_score:
            best_score = score
            best_move = move

    return best_move


@register_algorithm("overlap_max")
def choose_move(
    available: list[int],
    own_moves: list[int],
    opp_moves: list[int],
    k: int
) -> int:
    # Build the universe of numbers and all length‐k APs
    universe = sorted(set(available) | set(own_moves) | set(opp_moves))
    all_aps = [set(ap) for ap in find_all_arithmetic_progressions(k, universe)]

    # Filter to APs still possible for each side
    possible_self = [ap for ap in all_aps if not (ap & set(opp_moves))]
    possible_opp  = [ap for ap in all_aps if not (ap & set(own_moves))]

    # If truly no one can win, just play random
    if not possible_self and not possible_opp:
        return random.choice(available)

    # Helper: find (max_overlap, list_of_APs) for a given set of APs & moves
    def best_aps(aps: list[set[int]], moves: list[int]) -> tuple[int, list[set[int]]]:
        overlaps = [(len(ap & set(moves)), ap) for ap in aps]
        max_ov = max((ov for ov, _ in overlaps), default=0)
        best = [ap for ov, ap in overlaps if ov == max_ov]
        return max_ov, best

    self_ov, self_best = best_aps(possible_self, own_moves)
    opp_ov,  opp_best  = best_aps(possible_opp, opp_moves)

    # Offense if we're at least as close as they are
    if self_ov >= opp_ov and self_best:
        # Count frequency of each candidate number in our best APs
        freq: dict[int,int] = {}
        for ap in self_best:
            for num in ap:
                if num in available:
                    freq[num] = freq.get(num, 0) + 1
        if freq:
            maxf = max(freq.values())
            choices = [n for n,f in freq.items() if f == maxf]
            return random.choice(choices)

    # Defense otherwise
    if opp_best:
        freq = {}
        for ap in opp_best:
            for num in ap:
                if num in available:
                    freq[num] = freq.get(num, 0) + 1
        if freq:
            maxf = max(freq.values())
            choices = [n for n,f in freq.items() if f == maxf]
            return random.choice(choices)

    # Only if only draw condition
    return random.choice(available)




def compare(a: List[int], b: List[int]) -> bool:
    if len(a) != len(b):
        return False
    for i in range(len(a)):
        if a[i] != b[i]:
            return False
    return True


prev_root = None


@register_algorithm("mcts_cached")
def choose_move(
    available_moves: List[int],
    current_held: List[int],
    opponent_held: List[int],
    k: int,
) -> int:
    root = None
    global prev_root
    if prev_root is not None:
        for child in prev_root.children:
            if compare(child.current, current_held) and compare(
                child.opponent, opponent_held
            ):
                root = child
                root.parent = None
                break
    if not root:
        root = MCTSNode(available_moves, current_held, opponent_held, True, k)

    for _ in range(1000):  # number of simulations
        node = root

        # Selection
        while not node.is_terminal() and node.is_fully_expanded():
            node = node.best_child()

        # Expansion
        if not node.is_terminal() and not node.is_fully_expanded():
            node = node.expand()

        # Simulation
        result = node.rollout()

        # Backpropagation
        node.backpropagate(result)

    # Choose the move with the most visits
    best_child = max(root.children, key=lambda c: c.visits)
    prev_root = best_child
    return best_child.move


@register_algorithm("mcts")
def choose_move(
    available_moves: List[int],
    current_held: List[int],
    opponent_held: List[int],
    k: int,
) -> int:
    root = MCTSNode(available_moves, current_held, opponent_held, True, k)

    for _ in range(1000):  # number of simulations
        node = root

        # Selection
        while not node.is_terminal() and node.is_fully_expanded():
            node = node.best_child()

        # Expansion
        if not node.is_terminal() and not node.is_fully_expanded():
            node = node.expand()

        # Simulation
        result = node.rollout()

        # Backpropagation
        node.backpropagate(result)

    # Choose the move with the most visits
    best_child = max(root.children, key=lambda c: c.visits)
    return best_child.move
