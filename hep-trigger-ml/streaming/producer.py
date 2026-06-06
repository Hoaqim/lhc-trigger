import os, json, time, pandas as pd
from kafka import KafkaProducer

p = KafkaProducer(bootstrap_servers=os.environ["KAFKA_BROKERS"].split(","),
                  value_serializer=lambda v: json.dumps(v).encode())
df = pd.read_csv(os.environ.get("DATA", "HIGGS.csv"), header=None, nrows=500_000)
rate = float(os.environ.get("EVENTS_PER_SEC", 500))
for _, row in df.iterrows():
    p.send("events", {"features": row[1:].tolist(), "truth": int(row[0])})
    time.sleep(1/rate)