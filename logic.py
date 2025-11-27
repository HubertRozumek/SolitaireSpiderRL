import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

# CONFIG
NUM_SUITS = 1
NUM_COLUMNS = 1
NUM_CARDS = 104 # 2 decks

@dataclass
class Card:

    rank: int
    suit: int
    face_up: bool

    def __repr__(self):
        vals = {1: 'A', 11: 'J', 12: 'Q', 13: 'K'}
        r = vals.get(self.rank, str(self.rank))
        return f'[{r}]' if self.face_up else '[#]'


class Logic:

    def __init__(self):
        self.columns: List[List[Card]] = [[] for _ in range(NUM_COLUMNS)]
        self.stock: List[Card] = []
        self.foundation_count = 0
        self.history = []
        self.reset()

    def reset(self):
        pass

    def get_legal_moves(self):
        pass

    def apply_action(self,action):
        pass

    def _check_completed_sets(self):
        pass
