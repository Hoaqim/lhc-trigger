import os, json, boto3
ddb = boto3.resource("dynamodb").Table(os.environ["TABLE"])

def handler(event, context):
    item = ddb.get_item(Key={"pk": "stats"}).get("Item", {})
    n = int(item.get("n", 0)) or 1
    return {"statusCode": 200, "headers": {"content-type": "application/json"},
            "body": json.dumps({
                "events": int(item.get("n", 0)),
                "signal_fraction": round(int(item.get("signal", 0)) / n, 3),
                "live_accuracy":   round(int(item.get("correct", 0)) / n, 3),
                "scores": json.loads(item.get("recent", "[]"))})}