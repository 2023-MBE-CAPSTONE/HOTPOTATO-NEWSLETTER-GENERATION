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

    table = dynamodb.Table("issue_keyword")
    response = table.query(KeyConditionExpression=Key("issue_date").eq(today_date))['Items'][0]

    issue_name = response["issue_name"]
    negative_keyword = response["negative_keyword_list"]
    positive_keyword = response["positive_keyword_list"]

    print(f"생성할 뉴스레터 주제:{issue_name}")

    # make prompt
    ## output
    response_schemas = [
        ResponseSchema(name="positive_article", description="긍정 담론에 대한 뉴스레터"),
        ResponseSchema(name="positive_article_title", description="긍정 담론에 대한 쉽고 자극적인 뉴스레터의 제목"),
        ResponseSchema(name="negative_article", description="부정 담론에 대한 뉴스레터"),
        ResponseSchema(name="negative_article_title", description="부정 담론에 대한 쉽고 자극적인 뉴스레터의 제목"),
    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()
    ## input
    human_template = """
    너는 이슈와 이슈를 잘 나타내는 대표 키워드를 기반으로 이슈에 대한 반론을 친근한 반말 뉴스레터로 만드는 작가야
    뉴스레터를 생성할 때 모든 문장 사이에 개행 문자를 넣어줘
    이슈 : {issue_name} 
    긍정입장 대표 키워드: {positive_keyword}
    부정입장 대표 키워드: {negative_keyword}
    {format_instructions}
    """
    prompt = PromptTemplate(
        template=human_template,
        input_variables=["issue_name","positive_keyword","negative_keyword"],
        partial_variables={"format_instructions": format_instructions}
    )
    # load model
    llm = OpenAI(temperature=0.5,               # 창의성 (0.0 ~ 2.0) 
                 max_tokens=2048,             # 최대 토큰수
                 model_name='gpt-4',  # 모델명
    )
    # get output
    _input = prompt.format_prompt(
        issue_name=issue_name,
        positive_keyword=positive_keyword,
        negative_keyword=negative_keyword,
    )
    start_time = time.time()
    output = llm(_input.to_string())
    end_time = time.time()
    execution_time = end_time - start_time

    # 실행 시간을 출력합니다.
    print(f"뉴스레터 생성 소요 시간: {execution_time} 초")
    json_data = output_parser.parse(output)
    print(json_data['positive_article'])

    item = {
            "issue_date": today_date,
            "issue_name": issue_name,
            "positive_article": json_data["positive_article"],
            "positive_article_title": json_data["positive_article_title"],
            "negative_article": json_data["negative_article"],
            "negative_article_title": json_data["negative_article_title"],
    }
    print(item)
    # db에 insert
    generated_article_table = dynamodb.Table("generated_article")
    generated_article_table.put_item(

    Item=item

    ) 
    response = generated_article_table.query(KeyConditionExpression=Key("issue_date").eq("20231101")) 
    print(response['Items'][0])