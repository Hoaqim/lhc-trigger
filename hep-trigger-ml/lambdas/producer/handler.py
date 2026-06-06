import os, json, csv, io, random, boto3
sqs = boto3.client("sqs"); s3 = boto3.client("s3")
rows = list(csv.reader(io.StringIO(s3.get_object(
    Bucket=os.environ["DATA_BUCKET"],
    Key=os.environ.get("DATA_KEY", "data/HIGGS_sample.csv"))["Body"].read().decode())))

def handler(event, context):
    sample = random.sample(rows, min(int(os.environ.get("BATCH", 50)), len(rows)))
    for i in range(0, len(sample), 10):
        sqs.send_message_batch(QueueUrl=os.environ["QUEUE_URL"], Entries=[
            {"Id": str(j), "MessageBody": json.dumps(
                {"features": [float(v) for v in r[1:]], "truth": int(float(r[0]))})}
            for j, r in enumerate(sample[i:i+10])])
    return {"sent": len(sample)}