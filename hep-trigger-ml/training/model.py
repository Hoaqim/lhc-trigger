import torch.nn as nn

class HiggsMLP(nn.Module):
    def __init__(self, n_features=28):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features,256), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(256,128), nn.ReLU(),
            nn.Linear(128,1)
        )

        def forward(self, x): return self.net(x)