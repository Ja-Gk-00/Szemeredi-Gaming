from typing import List, Optional
import random
import math

from utils import find_all_arithmetic_progressions


class MCTSNode:
    def __init__(
        self,
        available: List[int],
        current: List[int],
        opponent: List[int],
        is_player_turn: bool,
        k: int,
        available_aps: Optional[List[set[int]]] = None,
    ):
        """
        Tree node for Monte Carlo Tree Search.

        :param available: numbers still on the board
        :param current:   numbers held by the player whose turn it is at this node
        :param opponent:  numbers held by the other player
        :param is_player_turn: whether it's 'current' player's turn
        :param k:         target progression length
        :param available_aps:
               if provided, a precomputed list of all arithmetic progressions (as sets)
               of length k over the union of available/current/opponent;
               otherwise it will be computed once here.
        """
        self.available = available
        self.current = current
        self.opponent = opponent
        self.k = k
        self.is_player_turn = is_player_turn

        # MCTS statistics
        self.visits = 0
        self.wins = 0

        # Tree structure
        self.children: List["MCTSNode"] = []
        self.untried_moves = available[:]
        self.parent: Optional["MCTSNode"] = None
        self.move: Optional[int] = None  # The move that led to this node

        # Ensure available_aps is defined exactly once
        if available_aps is None:
            # Compute all k‐length progressions over the combined set of seen numbers
            universe = set(available) | set(current) | set(opponent)
            raw_aps = find_all_arithmetic_progressions(self.k, sorted(universe))
            available_aps = [set(ap) for ap in raw_aps]
        self.available_aps = available_aps

    def expand(self) -> "MCTSNode":
        """Add one child by taking an untried move."""
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
            available=next_available,
            current=next_current if self.is_player_turn else self.current,
            opponent=next_opponent if not self.is_player_turn else self.opponent,
            is_player_turn=not self.is_player_turn,
            k=self.k,
            available_aps=self.available_aps,
        )
        child.parent = self
        child.move = move
        self.children.append(child)
        return child

    def is_fully_expanded(self) -> bool:
        """True if no moves remain to expand."""
        return len(self.untried_moves) == 0

    def best_child(self, c_param: float = 1.4) -> "MCTSNode":
        """
        Select the child with highest UCT value.
        """
        return max(
            self.children,
            key=lambda child: (
                child.wins / child.visits
                + c_param * math.sqrt(math.log(self.visits) / child.visits)
            ),
        )

    def rollout_policy(self, available: List[int]) -> int:
        """Default random rollout policy."""
        return random.choice(available)

    def is_terminal(self) -> bool:
        """Game over if no moves remain or someone has a progression."""
        return (
            not self.available
            or self.has_ap(self.current)
            or self.has_ap(self.opponent)
        )

    def has_ap(self, seq: List[int]) -> bool:
        """Check if seq contains any of the precomputed APs."""
        s = set(seq)
        return any(ap.issubset(s) for ap in self.available_aps)

    def rollout(self) -> float:
        """
        Simulate a game to completion by random play.
        Returns 1 for a win by the starting player,
                0 for a loss, and 0.5 for a draw.
        """
        current = self.current[:]
        opponent = self.opponent[:]
        available = self.available[:]
        turn = self.is_player_turn

        while available:
            move = self.rollout_policy(available)
            available.remove(move)
            if turn:
                current.append(move)
                if self.has_ap(current):
                    return 1.0
            else:
                opponent.append(move)
                if self.has_ap(opponent):
                    return 0.0
            turn = not turn
        return 0.5

    def backpropagate(self, result: float) -> None:
        """Propagate rollout result up the tree."""
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(result)
