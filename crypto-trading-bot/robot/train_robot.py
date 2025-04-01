import argparse
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from .trading_env import TradingEnv  # adjust import to your project
import os

device = "cpu"


def train_rl_agent(token="BTC", model_save_root="models/ppo_trading_agent"):
    token = token.upper()
    env = make_vec_env(lambda: TradingEnv(token), n_envs=1)
    metadata = {"render.modes": []}
    model = PPO(
        policy="MlpPolicy",
        env=env,
        verbose=1,
        device=device,
        tensorboard_log=f"./tensorboard_logs/{token}"
    )

    print(f"📈 Starting RL training for {token}...")
    model.learn(total_timesteps=100_000)

    token_model_path = os.path.join(model_save_root, token)
    os.makedirs(token_model_path, exist_ok=True)
    model_filename = f"ppo_trading_{token}"
    model.save(os.path.join(token_model_path, model_filename))

    print(f"✅ Model saved to {token_model_path}/{model_filename}.zip")

    return model

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", type=str, default="BTC", help="Token symbol (e.g. BTC, ETH, SOL)")
    args = parser.parse_args()

    train_rl_agent(token=args.token.upper())