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

        moves = []

        for s_idx, src_col in enumerate(self.columns):
            if not src_col: continue

            valid_stack_height = 0
            for i in range(len(src_col) - 1, -1, -1):
                if not src_col[i].face_up: break
                if i < len(src_col) -1:
                    if src_col[i].rank != src_col[i+1].rank +1:
                        break
                valid_stack_height += 1

            moving_card = src_col[-valid_stack_height]

            for t_idx, tgt_col in enumerate(self.columns):
                if s_idx == t_idx: continue

                if not tgt_col:
                    moves.append((s_idx, t_idx))
                else:
                    target_card = tgt_col[-1]
                    if target_card.rank == moving_card.rank + 1:
                        moves.append((s_idx, t_idx))

        if self.stock:
            empty_cols = any(len(c) == 0 for c in self.columns)
            if not empty_cols:
                moves.append((-1, -1))

        return moves

    def apply_action(self,action):

        src, tgt = action
        reward = 0

        if src == -1:
            if not self.stock: return -10

            for col in self.columns:
                if self.stock:
                    c = self.stock.pop()
                    c.face_up = True
                    col.append(c)

            self._check_completed_sets()
            return 2

        if not self.columns[src]: return -10

        move_idx = -1
        curr_rank = self.columns[src][-1].rank

        for i in range(len(self.columns[src]) -2, -1, -1):
            card = self.columns[src][i]
            if not card.face_up:
                move_idx = i + 1
                break
            if card.rank != curr_rank + 1:
                move_idx = i + 1
                break
            curr_rank = card.rank

            if move_idx == -1: move_idx = 0

            moving_stack = self.columns[src][move_idx:]
            top_moving = moving_stack[0]

            valid_target = False
            if not self.columns[tgt]: valid_target = True
            elif self.columns[tgt][-1].rank == top_moving.rank + 1: valid_target = True

            if not valid_target:
                return -10

            self.columns[tgt].extend(moving_stack)
            self.columns[src] = self.columns[src][:move_idx]

            reward = 5

            if self.columns[src] and not self.columns[src][-1].face_up:
                self.columns[src][-1].face_up = True
                reward += 20

            reward += self._check_completed_sets()

            return reward

    def _check_completed_sets(self):
        sets_found_reward = 0
        for col in self.columns:
            if len(col) < 13: continue

            is_seq = True
            last_13 = col[-13:]

            if last_13[0].rank != 13 or last_13[-1].rank + 1:
                continue

            for i in range(12):
                if last_13[i].rank != last_13[i+1].rank + 1:
                    is_seq = False
                    break

            if is_seq:
                for _ in range(13): col.pop()
                self.foundation_count += 1
                sets_found_reward += 100

                if col and not col[-1].face_up:
                    col[-1].face_up = True
                    sets_found_reward += 20

        return sets_found_reward

