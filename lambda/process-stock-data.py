import json
import base64
import boto3
from decimal import Decimal
import os

s3 = boto3.client("s3")
ddb = boto3.resource("dynamodb")
sns = boto3.client("sns")

RAW_BUCKET = os.environ['RAW_BUCKET']
TABLE_NAME = os.environ['TABLE_NAME']
SNS_TOPIC = os.environ['SNS_TOPIC']

table = ddb.Table(TABLE_NAME)

def lambda_handler(event, context):

    for rec in event['Records']:
        payload = base64.b64decode(rec['kinesis']['data']).decode('utf-8')
        data = json.loads(payload)

        symbol = data["symbol"]
        price  = data["price"]
        ts     = data["timestamp"]

        # 1. Store RAW record in S3
        s3.put_object(
            Bucket=RAW_BUCKET,
            Key=f"{symbol}/{ts}.json",
            Body=json.dumps(data)
        )

        # 2. Store processed record in DynamoDB
        table.put_item(Item={
            "symbol": symbol,
            "timestamp": ts,
            "price": Decimal(str(price))
        })

        # 3. Simple anomaly alert
        if price > 3500:
            sns.publish(
                TopicArn=SNS_TOPIC,
                Subject="Price Alert",
                Message=f"{symbol} crossed threshold: {price}"
            )

    return {"status": "OK"}
