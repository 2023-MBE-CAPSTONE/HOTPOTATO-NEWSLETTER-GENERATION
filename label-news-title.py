from dotenv import load_dotenv
from boto3.dynamodb.conditions import Key
from langchain.llms import OpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate
import boto3

import os
import time

from datetime import datetime



if __name__ == "__main__":
    # load issue and issue keyword from DB
    load_dotenv(verbose=True)
   
    dynamodb = boto3.resource(
        "dynamodb", 
        region_name=os.getenv("AWS_REGION_NAME"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    # get today date
    today = datetime.now()
    today_date = today.strftime('%Y%m%d')

    table = dynamodb.Table("generated_article")
    response = table.query(KeyConditionExpression=Key("issue_date").eq(today_date))['Items'][0]

    issue_name = response["issue_name"]
    negative_article = response["negative_article"]
    positive_article = response["positive_article"]


    news_title_table = dynamodb.Table("news_title")
    response = news_title_table.query(KeyConditionExpression=Key("issue_date").eq(today_date))['Items'][0]

    news_title_list = response["news_title_list"]
  
    print(f"생성할 뉴스레터 주제:{issue_name}")

    # make prompt
    ## output
    response_schemas = [
        ResponseSchema(name="news_title_label_list", description="뉴스 제목을 key, 레이블 결과를 value로 갖는 json들이 들어있는 리스트")
    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()

    ## input
    human_template = """
    너는 이슈에 대한 찬성, 반대 반론을 참고해서 뉴스의 제목 20개를
    "긍정"  또는  "부정" 또는 "판단할 수 없음"  3가지로 라벨링하는 레이블러야
    너가 레이블링해야하는 뉴스의 제목은 아래 뉴스 제목 리스트에 담겨 있어.
    이슈 : {issue_name} 
    이슈에 대한 긍정입장 담론: {positive_article}
    이슈에 대한 부정입장 담론: {negative_article}
    뉴스 제목 리스트: {news_title_list}
    {format_instructions}
    """
    prompt = PromptTemplate(
        template=human_template,
        input_variables=["issue_name","positive_article","negative_article","news_title_list"],
        partial_variables={"format_instructions": format_instructions}
    )
    # load model
    llm = OpenAI(temperature=0,               # 창의성 (0.0 ~ 2.0) 
                 max_tokens=2048,             # 최대 토큰수
                 model_name='gpt-4',  # 모델명
    )
    # get output
    _input = prompt.format_prompt(
        issue_name=issue_name,
        positive_article=positive_article,
        negative_article=negative_article,
        news_title_list=news_title_list,
    )
    start_time = time.time()
    output = llm(_input.to_string())
    end_time = time.time()
    execution_time = end_time - start_time

    # 실행 시간을 출력합니다.
    print(f"레이블 생성 소요 시간: {execution_time} 초")
    json_data = output_parser.parse(output)
    print(json_data['news_title_label_list'])

    
    # db에 insert
    response = news_title_table.update_item(
            Key={
                'issue_date': "20231102",
                'issue_name': '의대 정원 확대'
            },
            AttributeUpdates={
              'news_title_label_list': {
                'Value': json_data['news_title_label_list'],
                'Action': 'PUT'
              }
            }
        )
    print(response)