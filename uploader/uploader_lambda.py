import json
import boto3
import pandas as pd
from io import StringIO
from aws_upload import upload_to_rds

def lambda_handler(event, context):
    print("Lambda started")

    try:
        print("Fetching from S3...")
        s3 = boto3.client("s3")
        obj = s3.get_object(Bucket="music-scraper", Key="latest_scrape.csv")
        print("S3 fetch complete")

        csv_data = obj["Body"].read().decode("utf-8")
        df = pd.read_csv(StringIO(csv_data))
        print(f"DataFrame loaded, shape: {df.shape}")

    except Exception as e:
        print(f"Error fetching/reading from S3: {e}")
        raise

    try:
        upload_to_rds(df)
        
    except Exception as e:
        print(f"Error uploading to RDS: {e}")
        raise

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Upload attempted", "rows": len(df)})
    }
