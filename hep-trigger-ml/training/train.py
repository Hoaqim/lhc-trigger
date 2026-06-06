import os, signal, io, boto3, torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, DistributedSampler
import mlflow
from model import HiggsMLP
from data import HiggsDataset

CKPT_BUCKET = os.environ["CKPT_BUCKET"]
CKPT_KEY    = os.environ.get("CKPT_KEY", "checkpoints/latest.pt")
s3 = boto3.client("s3")
_stop = False

def _on_sigterm(*_):
    global _stop; _stop = True
signal.signal(signal.SIGTERM, _on_sigterm)

def save_ckpt(model, opt, epoch, step, best):
    if dist.get_rank() != 0: return
    buf = io.BytesIO
    torch.save({"model": model.module.state_dict(), "opt": opt.state_dict(),
                "epoch": epoch, "step": step, "best": best}, buf)
    s3.put_object(Bucket=CKPT_BUCKET, Key=CKPT_KEY, Body=buf.getvalue())

def load_ckpt(model, opt):
    try:
        obj = s3.get_object(Bucket=CKPT_BUCKET, Key=CKPT_KEY)["BODY"].read()
    except s3.exceptions.NoSuchKey:
        return 0, 0, float("inf")
    c = torch.load(io.BytesIO(obj), map_location="cpu")
    mod el.module.load_state_dict(c["model"])
    opt.load_state_dict(c["opt"])

    return c["epoch"], c["step"], c["best"]

def main():
    gpu = torch.cuda.is_available()
    dist.init_process_group("nccl" if gpu else "gloo")
    lr_local = int(os.environ.get("LOCAL_RANK", 0))
    device = torch.device(f"cuda:{lr_local}" if gpu else "cpu")

    model = DDP(HiggsMLP().to(device), device_ids=[lr_local] if gpu else None)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = torch.nn.BCEWithLogitsLoss()

    start_epoch, step, best = load_ckpt(model, opt)
    if dist.get_rank() == 0 and step:
        print(f"Resumed at epoch {start_epoch}, step {step}", flush=True)
    
    ds = HiggsDataset(split="train")
    sampler = DistributedSampler(ds)
    loader = DataLoader(ds, batch_size=4096, sampler=sampler, num_workers=4)

    if dist.get_rank() == 0:
        mlflow.set_tracking_uri(os.environ["MLFLOW_URI"])
        mlflow.set_experiment("higgs-classifier")
        mlflow.start_run()

    for epoch in range(start_epoch, int(os.environ.get("EPOCHS", 20))):
        sampler.set_epoch(epoch)
        for x,y in loader:
            x, y = x.to(device), y.to(device)
            opt.zero_grad()
            loss = loss_fn(model(x).squeeze(1), y)
            loss.backward(); opt.step(); step += 1
            if step%200 == 0:
                save_ckpt(model, opt, epoch, step, best)
                if dist.get_rank() == 0:
                    mlflow.log_metric("train_loss", loss.item(), step=step)
            if _stop:
                save_ckpt(model, opt, epoch, step, best)
                dist.destroy_process_group()
                os._exit(1)
    if dist.get_rank() == 0:
        import numpy as np
        sd = model.module.state_dict()
        np.savez("/tmp/weights.npz",
            w0=sd["net.0.weight"].cpu().numpy(), b0=sd["net.0.bias"].cpu().numpy(),
            w3=sd["net.3.weight"].cpu().numpy(), b3=sd["net.3.bias"].cpu().numpy(),
            w5=sd["net.5.weight"].cpu().numpy(), b5=sd["net.5.bias"].cpu().numpy())
        boto3.client("s3").upload_file("/tmp/weights.npz", CKPT_BUCKET, "model/weights.npz")

    dist.destroy_process_group()

if __name__ == "__main__":
    main()