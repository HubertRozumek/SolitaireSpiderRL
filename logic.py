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
        self.columns = [[] for _ in range(NUM_COLUMNS)]
        self.stock = []
        self.foundation_count = 0

        full_deck = [Card(rank, 0) for rank in range(1, 14) for _ in range(8)]
        random.shuffle(full_deck)

        for i in range(54):
            col_idx = i % NUM_COLUMNS
            card = full_deck.pop()

            if i >= 44:
                card.face_up = True
            elif i < 44:
                card.face_up = False

            self.columns[col_idx].append(card)

        for col in self.columns:
            if col: col[-1].face_up = True

        self.stock = full_deck

    def get_legal_moves(self):
        pass

    def apply_action(self,action):
        pass

    def _check_completed_sets(self):
        pass
