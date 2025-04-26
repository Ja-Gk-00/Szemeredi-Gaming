from typing import List, Optional
import random
import math

from utils import find_all_arithmetic_progressions

class MCTSNode:
    def __init__(self, available: List[int], current: List[int], opponent: List[int], is_player_turn: bool, k: int, available_aps: Optional[List[set[int]]] = None):
        self.available = available
        self.current = current
        self.opponent = opponent
        self.k = k
        self.is_player_turn = is_player_turn
        self.visits = 0
        self.wins = 0
        self.children: List[MCTSNode] = []
        self.untried_moves = available[:]
        self.parent: Optional[MCTSNode] = None
        self.move = None  # The move that led to this node
        if availble_aps is None:
            availble_aps = [set(ap) for ap in find_all_arithmetic_progressions(k, list({n for n in available + current + opponent}))]
        self.availble_aps = availble_aps

    def expand(self):
        move = self.untried_moves.pop()
        next_available = self.available[:]
        next_available.remove(move)
        next_current = self.current[:]
        next_opponent = self.opponent[:]

        if self.is_player_turn:
            next_current.append(move)
        else:
            next_opponent.append(move)

        child = MCTSNode(
            next_available,
            next_current if self.is_player_turn else self.current,
            next_opponent if not self.is_player_turn else self.opponent,
            not self.is_player_turn,
            self.k,
            self.availble_aps
        )
        child.parent = self
        child.move = move
        self.children.append(child)
        return child

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def best_child(self, c_param=1.4):
        return max(self.children, key=lambda child: child.wins / child.visits + c_param * math.sqrt(math.log(self.visits) / child.visits))

    def rollout_policy(self, available: List[int]) -> int:
        return random.choice(available)

    def is_terminal(self):
        return len(self.available) == 0 or self.has_ap(self.current, self.k) or self.has_ap(self.opponent, self.k)

    def has_ap(self, seq: List[int], k: int) -> bool:
        s = set(seq)
        return any(ap.issubset(s) for ap in self.availble_aps)

    def rollout(self):
        current = self.current[:]
        opponent = self.opponent[:]
        available = self.available[:]
        turn = self.is_player_turn

        while available:
            move = self.rollout_policy(available)
            available.remove(move)
            if turn:
                current.append(move)
                if self.has_ap(current, self.k):
                    return 1  # win
            else:
                opponent.append(move)
                if self.has_ap(opponent, self.k):
                    return 0  # loss
            turn = not turn
        return 0.5  # draw

    def backpropagate(self, result):
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(result)