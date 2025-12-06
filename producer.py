import boto3
import json
import time
import random
from datetime import datetime

kinesis = boto3.client("kinesis", region_name="us-east-1")
STREAM = "stock-stream"

symbols = ["AAPL", "MSFT", "GOOG", "AMZN"]

# initial prices
prices = {
    "AAPL": 150.0,
    "MSFT": 320.0,
    "GOOG": 2800.0,
    "AMZN": 3500.0
}

while True:
    for sym in symbols:
        # simulate price movement
        change = random.uniform(-2, 2)
        prices[sym] += change

        record = {
            "symbol": sym,
            "price": round(prices[sym], 2),
            "timestamp": datetime.utcnow().isoformat()
        }

        kinesis.put_record(
            StreamName=STREAM,
            Data=json.dumps(record),
            PartitionKey=sym
        )

        print("Sent:", record)

    time.sleep(2)
