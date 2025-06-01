import json
import boto3
import pandas as pd
from io import StringIO
from main import main

def lambda_handler(event, context):
    events = main()

    if events.empty:
        return {
            "statusCode": 204,
            "body": json.dumps({"message": "No events found."})
        }

    csv_buffer = StringIO()
    events.to_csv(csv_buffer, index=False)
    
    s3 = boto3.client("s3")
    s3.put_object(
        Bucket="music-scraper",
        Key="latest_scrape.csv",
        Body=csv_buffer.getvalue()
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Scrape uploaded to S3", "rows": len(events)})
    }
