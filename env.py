import gymnasium as gym
from gymnasium import spaces
import numpy as np
from logic import Logic, NUM_COLUMNS

class Env(gym.Env):

    def __init__(self, render_mode=None):
        super(Env, self).__init__()
        self.game = Logic()
        self.render_mode = render_mode

        self.action_space = spaces.Discrete(101)

        self.max_rows = 20
        self.observation_space = spaces.Box(
            low=0, high=13,
            shape = (NUM_COLUMNS, self.max_rows, 2),
            dtype=np.float32
        )

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.game.reset()
        return self._get_obs(), {}

    def step(self, action):
        reward = 0
        terminated = False
        action_desc = "Illegal action"
        move = (0, 0)

        if action == 100:
            move = (-1, -1)
            action_desc = "Deal"
        elif 0 <= action <= 99:
            src = action // 10
            tgt = action % 10

            if 0 <= src < 10 and 0 <= tgt < 10:
                move = (src, tgt)
                action_desc = f"{src}->{tgt}"
            else:
                reward = -100
                observation = self._get_obs()
                return observation, reward, terminated, False, {}
        else:
            reward = -100
            observation = self._get_obs()
            return observation, reward, terminated, False, {}

        reward = self.game.apply_action(move)
        reward -= 0.1

        terminated = False
        if self.game.foundation_count == 8:
            terminated = True
            reward += 1000

        observation = self._get_obs()

        if self.render_mode == 'console':
            print(f"Action: {action_desc} | Reward: {reward} | Sets: {self.game.foundation_count}")

        return observation, reward, terminated, False, {}

    def _get_obs(self):

        obs = np.zeros((NUM_COLUMNS, self.max_rows, 2), dtype=np.float32)

        for i, col in enumerate(self.game.columns):
            for j, card in enumerate(col):
                if j >= self.max_rows: break

                if card.face_up:
                    obs[i,j,0] = card.rank
                    obs[i,j,1] = 1.0
                else:
                    obs[i,j,0] = 0.0
                    obs[i,j,1] = 0.0

        return obs

    def action_masks(self):

        mask = np.zeros(self.action_space.n, dtype=bool)

        legal_moves = self.game.get_legal_moves()

        for src, tgt in legal_moves:
            if src == -1:
                mask[100] = True

            else:
                action_index = src * 10 + tgt
                mask[action_index] = True

        return mask