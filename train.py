import os
from sb3_contrib import MaskablePPO
from env import Env

def train():

    env = Env(render_mode=None)

    print("Initializing...")
    model = MaskablePPO("MlpPolicy", env, verbose=1, learning_rate=1e-3, n_steps=2048)

    print("Training...")
    model.learn(total_timesteps=int(300000))

    model_path =  "spider_solitaire_ppo"
    model.save(model_path)
    print("Model saved!")


if __name__ == "__main__":
    train()