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

    table = dynamodb.Table('news_title')
 
    

    # table.put_item(

    # Item={
    #         "issue_date": "20231102",
    #         "issue_name": "의대 정원 확대",
    #         "news_title_list": [
    #         "2006년 이후 그대로 의대 증원 둘러싼 '저출산 고령화'",
    #         "의료파업에 번번이 증원 ‘백기’ “의정협의체 거쳐야” vs “尹 국정과제”",
    #         "의대정원 확대 추진에 의협 “집단휴진” 경고 반발 돌파 묘수 있나",
    #         "친명 정성호 환영했는데 野 '의대 정원 확대' 침묵하는 이유",
    #         "[더뉴스] 17년 째 고정 한국 의대 정원, OECD '꼴찌 수준'...다른 나라는?",
    #         "보궐선거 참패 후 쏘아올린 의대정원 확대",
    #         "당정, 의대정원 파격 증원 의협 “파업 등 모든 수단으로 총력 대응”(종합)",
    #         "8. 민주당 의원, 이례적 尹 칭찬 “文정부도 겁먹고 못한 엄청난 일”",
    #         "국힘 최고위 '규제개혁 깃발 높은데 성과 미진' 정부에 쓴소리",
    #         "당정, 의대정원 확 늘리겠다 의사단체 '파업불사' 초강경 대응예고",
    #         "“국가가 해야할 일” vs “일방적 추진” 의대 정원 파격확대 가능할까",
    #         "늘어나는 의대 정원, 의사 태부족 지방 중심 배정될 전망",
    #         "정부, 의대 정원 ‘1000명 이상 확대’ 이번주 발표",
    #         "[사설]만시지탄인 의대 ‘정원 1000명’ 확대, 의협은 수용하라",
    #         "尹, 직접 1000명 수준 증원 발표하나... 총선 전 판 커진 의대 정원 늘리기",
    #         "의료계 반발 필수의료 체계 개선 의대정원 개편 '첩첩산중'",
    #         "정부 '의대 증원 1000명' 카드 꺼낸다  의사 파업 재현되나",
    #         "정부, 의대정원 ‘1000명 이상’ 확대안 발표 전망 의사단체 “투쟁”",
    #         "의대 정원 늘리기' 번번이 실패 의사들은 '반발'",
    #         "의대 정원 1천 명 이상 늘릴 듯' 전국 의대마다 증원",
    #     ],
    #     'news_title_label_list':[],
    # }

    # ) 
    response = table.query(KeyConditionExpression=Key("issue_date").eq("20231102")) 
    print(response['Items'][0])