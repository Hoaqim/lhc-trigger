
import os, json, io, boto3, numpy as np
s3  = boto3.client("s3")
ddb = boto3.resource("dynamodb").Table(os.environ["TABLE"])
_w = np.load(io.BytesIO(s3.get_object(
    Bucket=os.environ["MODEL_BUCKET"],
    Key=os.environ.get("MODEL_KEY", "model/weights.npz"))["Body"].read()))

def forward(x):                                    
    x = np.maximum(0, x @ _w["w0"].T + _w["b0"])
    x = np.maximum(0, x @ _w["w3"].T + _w["b3"])
    return 1.0 / (1.0 + np.exp(-(x @ _w["w5"].T + _w["b5"])))

def handler(event, context):
    n = signal = correct = 0
    scores = []
    for record in event["Records"]:               
        ev = json.loads(record["body"])
        p = float(forward(np.array(ev["features"], dtype=np.float32))[0])
        pred = int(p > 0.5)
        n += 1; signal += pred; correct += int(pred == ev["truth"])
        scores.append(round(p, 3))
    ddb.update_item(
        Key={"pk": "stats"},
        UpdateExpression="ADD #n :n, #sig :s, #cor :c SET recent = :r",
        ExpressionAttributeNames={"#n": "n", "#sig": "signal", "#cor": "correct"},
        ExpressionAttributeValues={":n": n, ":s": signal, ":c": correct,
                                   ":r": json.dumps(scores[-50:])})
 
    return {"scored": n}