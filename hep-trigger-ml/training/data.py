import torch ,pandas as pd
from torch.utils.data import Dataset

class HiggsDataset(Dataset):
    def __init__(self, path="HIGGS.csv", split="train", limit=2_000_000):
        df = pd.read_csv(path, header=None, nrows=limit)
        n = int(len(df) * 0.9)
        df = df.iloc[:n] if split == "train" else df.iloc[n:]
        self.y = torch.tensor(df[0].values, dtype=torch.float32)
        self.X = torch.tensor(df.iloc[:,1:].values, dtype=torch.float32)
    
    def __len__(self): return self.X.shape[0]
    def __getitem__(self, i): return self.X[i], self.y[i]