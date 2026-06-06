import os, json, threading, collections, time, torch, mlflow
from kafka import KafkaConsumer
from fastapi import FastAPI
import uvicorn

model = mlflow.pytorch.load_model(os.environ["MODEL_URI"]).eval()
S = {"n": 0, "sig": 0, "rate": 0.0, "correct":0,
     "scores": collections.deque(maxlen=2000)}

def consume():
    c = KafkaConsumer("events",
                      bootstrap_servers=os.environ["KAFKA_BROKERS"].split(","),
                      value_deserializer=lambda b: json.loads(b))
    
    t0, cnt = time.time(), 0
    for m in c:
        x = torch.tensor([m.value["features"]], dtype=torch.float32)
        with torch.no_grad():
            score = torch.sigmoid(model(x)).item()
        pred = int(score > 0.5)
        S["n"] += 1; S["sig"] += pred; S["scores"].append(score)
        S["correct"] += int(pred == m.value["truth"]); cnt+=1
        if time.time() - t0 >= 1:
            S["rate"] = cnt/ (time.time() - t0)
            t0, cnt = time.time(), 0

app = FastAPI()
@app.get("/stats")
def stats():
    n = max(S["n", 1])
    return {"events": S["n"], "events_per_sec": round(S["rate"], 1),
            "signal_fraction": round(S["sig"]/n, 3),
            "live_accuracy": round(S["correct"]/n, 3),
            "scores": list(S["scores"])}

threading.Thread(target=consume, daemon=True).start()
uvicorn.run(app, host="0.0.0.0", port=8000)