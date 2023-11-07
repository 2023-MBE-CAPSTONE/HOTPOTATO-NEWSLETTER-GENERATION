from dotenv import load_dotenv
from boto3.dynamodb.conditions import Key
from langchain.llms import OpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate
import boto3
from langchain import ConversationChain
import os
import time

from datetime import datetime



if __name__ == "__main__":
    # load issue and issue keyword from DB
    load_dotenv(verbose=True)
   

    issue_name = "의대 정원 확대"
    positive_keyword = [('의사/NNG', 62.72919701966553), ('의대/NNG', 29.97854648615543), ('증원/NNG', 12.100657124742062), ('국민/NNG', 10.326327171837375), ('안/NNG', 7.649449647220557), ('밥그릇/NNG', 7.311069344708176), ('반대/NNG', 7.02683583378657), ('때/NNG', 6.4979285429382365), ('돈/NNG', 6.474818739957368), ('지방/NNG', 6.202390266094542), ('정부/NNG', 6.1839562537667625), ('정원/NNG', 5.370666157339533), ('부족/NNG', 4.979483502888833), ('확대/NNG', 4.365493006529755), ('병원/NNG', 4.359168852445753), ('사람/NNG', 4.2275971054615455), ('필요/NNG', 4.170167497610597), ('협회/NNG', 4.079655869756441), ('의료/NNG', 4.045043618929863), ('생각/NNG', 4.033463269593962), ('나라/NNG', 3.9463728122655075), ('지/NNG', 3.9156070130940956), ('진료/NNG', 3.873026207536983), ('지지/NNG', 3.862868332954765), ('이상/NNG', 3.8343119458932535), ('이번/NNG', 3.790370962395639), ('기득/NNG', 3.724949126596758), ('과/NNG', 3.412108211330019), ('경쟁/NNG', 3.323063913735312), ('환자/NNG', 3.2786994015411572)]
    negative_keyword = [('의사/NNG', 43.233004976363276), ('의대/NNG', 19.150073115158992), ('부족/NNG', 9.347472709341659), ('문제/NNG', 9.105433193148697), ('지방/NNG', 8.984413435052081), ('안/NNG', 8.500334402665855), ('사람/NNG', 8.016255370279897), ('의료/NNG', 7.895235612183402), ('돈/NNG', 7.169117063604438), ('해결/NNG', 6.685038031218287), ('국민/NNG', 6.200958998832356), ('증원/NNG', 6.200958998832356), ('과/NNG', 5.9589194826393355), ('진료/NNG', 5.837899724542817), ('말/NNG', 5.232800934060239), ('병원/NNG', 5.1117811759637455), ('생각/NNG', 4.869741659770745), ('지원/NNG', 4.869741659770745), ('나라/NNG', 4.143623111191608), ('정원/NNG', 4.022603353095113), ('때/NNG', 4.022603353095113), ('환자/NNG', 3.5385243207091372), ('의료비/NNG', 3.4175045626125553), ('반대/NNG', 3.4175045626125553), ('정책/NNG', 3.4175045626125553), ('지역/NNG', 3.4175045626125553), ('정부/NNG', 3.296484804516081), ('인구/NNG', 3.0544452883230795), ('미용/NNG', 2.933425530226597), ('이유/NNG', 2.933425530226597)]
    # make prompt
    ## output
    response_schemas = [
        ResponseSchema(name="positive_article", description="긍정 담론에 대한 뉴스레터"),
        ResponseSchema(name="negative_article", description="부정 담론에 대한 뉴스레터"),
    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()
    ## input
    human_template = """
    각각의 키워드를 이용하여 이슈에 대한 담론을 만들어라.
    조건 : '반말'로 설득하면서 시선을 끌 수 있는 요소를 포함시켜라
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
    conversation = ConversationChain(llm=llm, verbose=True)
    output = conversation.predict(input=_input.to_string())
    end_time = time.time()
    execution_time = end_time - start_time

    # 실행 시간을 출력합니다.
    print(f"뉴스레터 생성 소요 시간: {execution_time} 초")
    json_data = output_parser.parse(output)
    print(json_data['positive_article'])

    # 
    response_schemas_2 = [
        ResponseSchema(name="labeled_newsletter_list", description="뉴스 제목을 key 레이블링 결과를 value로 하는 딕셔너리가 든 리스트"),
    ]
    output_parser_2 = StructuredOutputParser.from_response_schemas(response_schemas_2)
    format_instructions_2 = output_parser_2.get_format_instructions()
    ## input
    news_headlines = [
    "2006년 이후 그대로 의대 증원 둘러싼 '저출산 고령화'",
    "의료파업에 번번이 증원 ‘백기’ “의정협의체 거쳐야” vs “尹 국정과제”",
    "의대정원 확대 추진에 의협 “집단휴진” 경고 반발 돌파 묘수 있나",
    "친명 정성호 환영했는데 野 '의대 정원 확대' 침묵하는 이유",
    "[더뉴스] 17년 째 고정 한국 의대 정원, OECD '꼴찌 수준'...다른 나라는?",
    "보궐선거 참패 후 쏘아올린 의대정원 확대",
    "당정, 의대정원 파격 증원 의협 “파업 등 모든 수단으로 총력 대응”(종합)",
    "민주당 의원, 이례적 尹 칭찬 “文정부도 겁먹고 못한 엄청난 일”",
    "국힘 최고위 '규제개혁 깃발 높은데 성과 미진' 정부에 쓴소리",
    "당정, 의대정원 확 늘리겠다 의사단체 '파업불사' 초강경 대응예고",
    "“국가가 해야할 일” vs “일방적 추진” 의대 정원 파격확대 가능할까",
    "늘어나는 의대 정원, 의사 태부족 지방 중심 배정될 전망",
    "정부, 의대 정원 ‘1000명 이상 확대’ 이번주 발표",
    "[사설]만시지탄인 의대 ‘정원 1000명’ 확대, 의협은 수용하라",
    "尹, 직접 1000명 수준 증원 발표하나... 총선 전 판 커진 의대 정원 늘리기",
    "의료계 반발 필수의료 체계 개선 의대정원 개편 '첩첩산중'",
    "정부 '의대 증원 1000명' 카드 꺼낸다  의사 파업 재현되나",
    "정부, 의대정원 ‘1000명 이상’ 확대안 발표 전망 의사단체 “투쟁”",
    "의대 정원 늘리기' 번번이 실패 의사들은 '반발",
    "의대 정원 1천 명 이상 늘릴 듯' 전국 의대마다 증원"
    ]

    human_template2 = """
    위에서 생성한 긍정,부정 입장 담론을 참고해서 기사 제목  "긍정"  또는  "부정" 또는 "판단할 수 없음"  3가지로 라벨링하고, csv 형태로 추출해라(tab이용)
    기사 제목 : {news_title_list} 
    {format_instructions}
    """
    prompt2 = PromptTemplate(
        template=human_template2,
        input_variables=["news_title_list"],
        partial_variables={"format_instructions": format_instructions_2}
    )
    _input2 = prompt2.format_prompt(
        news_title_list=news_headlines,
    )
    output = conversation.predict(input=_input2.to_string())
    json_data = output_parser.parse(output)
    print(json_data['labeled_newsletter_list'])
    end_time = time.time()
    
    