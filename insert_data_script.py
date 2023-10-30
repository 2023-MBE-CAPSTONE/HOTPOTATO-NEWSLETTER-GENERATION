import boto3
from dotenv import load_dotenv
from boto3.dynamodb.conditions import Key
import os

if __name__ == "__main__":
    load_dotenv(verbose=True)
   
    dynamodb = boto3.resource(
        "dynamodb", 
        region_name=os.getenv("AWS_REGION_NAME"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )

    table = dynamodb.Table('issueKeyword')
    response = table.query(KeyConditionExpression=Key("issueDate").eq(20231030)) 
    print(response['Items'][0])