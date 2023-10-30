from dotenv import load_dotenv
from boto3.dynamodb.conditions import Key
from langchain.llms import OpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate
import boto3

import os
import time



if __name__ == "__main__":
    # load issue and issue keyword from DB
    load_dotenv(verbose=True)
   
    dynamodb = boto3.resource(
        "dynamodb", 
        region_name=os.environ("AWS_REGION_NAME"),
        aws_access_key_id=os.environ("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ("AWS_SECRET_ACCESS_KEY")
    )

    table = dynamodb.Table('issueKeyword')
    response = table.query(KeyConditionExpression=Key("issueDate").eq(20231030))['Items'][0]

    issue_name = response["issueName"]
    negative_keyword = response['negativeKeyword']
    positive_keyword = response['positiveKeyword']

    print(f"생성할 뉴스레터 주제:{issue_name}")

    # make prompt
    ## output
    response_schemas = [
        ResponseSchema(name="positive_article", description="긍정 담론에 대한 뉴스레터"),
        ResponseSchema(name="negative_article", description="부정 담론에 대한 뉴스레터")
    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()
    ## input
    human_template = """
    너는 이슈와 이슈를 잘 나타내는 대표 키워드를 기반으로 이슈에 대한 반론을 친근한 반말 뉴스레터로 만드는 작가야
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
    llm = OpenAI(temperature=0,               # 창의성 (0.0 ~ 2.0) 
                 max_tokens=2048,             # 최대 토큰수
                 model_name='gpt-4',  # 모델명
    )
    # get output
    _input = prompt.format_prompt(
        issue_name="의대 정원 확대",
        positive_keyword=["찬성", "특권", "이기적"],
        negative_keyword=["반대", "파업", "피부과"],
    )
    start_time = time.time()
    output = llm(_input.to_string())
    end_time = time.time()
    execution_time = end_time - start_time

    # 실행 시간을 출력합니다.
    print(f"뉴스레터 생성 소요 시간: {execution_time} 초")
    json_data = output_parser.parse(output)
    print(json_data['positive_article'])