import torch
from torch import nn
from torch.distributions import Categorical
import torch.nn.functional as F


class SimpleMLP(nn.Module):
    def __init__(self, input_size=(3, 480, 640), hidden_size=128, output_size=5, n_layers=2):
        super().__init__()

        self.input_layer = nn.Linear(input_size, hidden_size)
        
        self.hidden = nn.ModuleList()

        for _ in range(n_layers):  # Two hidden layers
            self.hidden.append(nn.Linear(hidden_size, hidden_size))
            self.hidden.append(nn.ReLU())

        self.output_layer = nn.Linear(hidden_size, output_size)
        

    def forward(self, X):
        X = X.flatten(start_dim=1)
        X = self.input_layer(X)
        for layer in self.hidden:
            X = layer(X)
        return self.output_layer(X)
import torch.nn as nn

class SimpleConv2d(nn.Module):
    def __init__(self, input_size=(3, 480, 640), hidden_size=32, output_size=5, n_layers=1):
        super().__init__()

        in_channels = input_size[0]
        layers = []

        for _ in range(n_layers):
            layers.append(nn.Conv2d(in_channels, hidden_size, kernel_size=3, padding=1))
            layers.append(nn.ReLU())
            layers.append(nn.MaxPool2d(kernel_size=2, stride=2))
            in_channels = hidden_size

        self.hidden = nn.Sequential(*layers)

        self.output_layer = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(hidden_size, output_size),
        )

    def forward(self, X):
        X = self.hidden(X)
        return self.output_layer(X)


class DoomTraining:
    def __init__(self, game, model, actions):
        self.game = game
        self.actions = actions
        self.model = model
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)


    def train(self, epochs=100, episodes=10, lr=0.001, gamma=0.99):
        losses = []
        for group in self.optimizer.param_groups:
            group["lr"] = lr

        for epoch in range(epochs):
            self.model.train()
            self.optimizer.zero_grad()

            trajectories = self.play_doom(episodes=episodes)
            all_log_probs = []
            all_returns = []
            episode_scores = []

            for log_probs, rewards, episode_score in trajectories:
                episode_scores.append(episode_score)
                discounted_returns = []
                return_so_far = 0.0
                for reward in reversed(rewards):
                    return_so_far = reward + gamma * return_so_far
                    discounted_returns.append(return_so_far)
                all_log_probs.extend(log_probs)
                all_returns.extend(reversed(discounted_returns))

            returns = torch.tensor(all_returns, dtype=torch.float32)
            returns = (returns - returns.mean()) / (returns.std(unbiased=False) + 1e-8)
            loss = -(torch.stack(all_log_probs) * returns).mean()
            loss.backward()
            self.optimizer.step()

            losses.append(loss.item())
            if (epoch + 1) % 10 == 0:
                mean_score = sum(episode_scores) / len(episode_scores)
                print(
                    f"Epoch [{epoch + 1}/{epochs}], "
                    f"Loss: {loss.item():.4f}, Mean score: {mean_score:.2f}"
                )

        return losses

    def play_doom(self, episodes=10):
        trajectories = []
        for episode in range(episodes):
            log_probs = []
            rewards = []
            print(f"Episode #{episode + 1}")
            self.game.new_episode()

            while not self.game.is_episode_finished():
                state = self.game.get_state()
                if state is not None and state.automap_buffer is not None:
                    observation = torch.as_tensor(state.automap_buffer, dtype=torch.float32).unsqueeze(0)
                    logits = self.model(observation)

                    distribution = Categorical(logits=logits)
                    action = distribution.sample()
                    log_probs.append(distribution.log_prob(action).squeeze(0))
                    rewards.append(float(self.game.make_action(self.actions[action.item()])))

            trajectories.append((log_probs, rewards, self.game.get_total_reward()))
        
        return trajectories
    


if __name__ == "__main__":
    import vizdoom  as vzd
    from vizdoom import DoomGame, Mode, ScreenFormat, ScreenResolution
    import os

    game = DoomGame()
    game.load_config("scenarios/basic.cfg")
    game.set_doom_scenario_path(os.path.join(vzd.scenarios_path, "basic.wad"))
    game.set_available_buttons([
            vzd.Button.MOVE_LEFT, 
            vzd.Button.MOVE_RIGHT,
            vzd.Button.MOVE_FORWARD,
            vzd.Button.MOVE_BACKWARD, 
            vzd.Button.ATTACK
        ])
    game.set_mode(Mode.PLAYER)
    game.set_screen_format(ScreenFormat.RGB24)
    game.set_screen_resolution(ScreenResolution.RES_640X480)
    
        
    game.init()

    actions = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0], [1, 0, 1]]
    model = SimpleConv2d(input_size=(3, 480, 640), hidden_size=32, output_size=len(actions), n_layers=1)
    trainer = DoomTraining(game, model, actions)

    losses = trainer.train(epochs=100, episodes=10)
    print("Training completed. Losses:", losses)