# requests 와 json 을 활용하여 slack bot 조작하기
import requests
import json
import datetime as dt
import time
from bs4 import BeautifulSoup

Token =  '' # 자신의 Token 입력

# 메시지를 보내는 부분. 함수 안 argument 순서 :
# token : Slack Bot의 토큰
# channel : 메시지를 보낼 채널 #stock_notice
# text : Slack Bot 이 보낼 텍스트 메시지. 마크다운 형식이 지원된다.
# attachments : 첨부파일. 텍스트 이외에 이미지등을 첨부할 수 있다.

def notice_message(token, channel, text, attachments = []): #봇에게 보내기
    attachments = json.dumps(attachments) # 리스트는 Json 으로 덤핑 시켜야 Slack한테 제대로 간다.
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel, "text": text ,"attachments": attachments})

def bring_news(): #뉴스 크롤링 
    title_list = []
    href_list = []
    img_list = []
    url = requests.get("https://media.naver.com/press/052/ranking?type=popular",# 불러올 주소 
                    headers={'User-Agent':'Mozilla/5.0'}) # 해당코드는 코드를 웹으로 접속하는것처험 하게 해주는 우회 코드
    html = BeautifulSoup(url.text, "html.parser") #html을 텍스트로 변환

    titles_html = html.select('.list_title') #기사 한글 제목 따오는 코드
    href_html = html.select('.as_thumb > a') #기사 링크 따오는 코드
    img_html = html.select('.list_img > img')#이미지 링크 따오는 코드

    for i in range(10):#기사제목 리스트에 추가
        title_list.append(titles_html[i].text)
        i+=1

    for k in href_html:#기사링크 리스트에 추가
        href = k.attrs['href']
        href_list.append(href)

    for img in img_html: # 기사사진링크 리스트에 추가
        img1 = img.attrs['src']
        img_list.append(img1)
    return title_list, href_list, img_list

def stock_code(): #시가총액 5위 종가가격
    codes =  [
    '005930', #삼성전자
    '000660', #sk하이닉스
    '373220',#lg에너지솔루션
    '207940', #삼성바이오로직스
    '051910' #lg화학
    ]
    price_all = [] #가격 모아둘 리스트
    for code in codes:
        url = f"https://finance.naver.com/item/sise.naver?code={code}"
        response = requests.get(url) #url을 얻기 위한 것
        html = response.text #html은 텍스트이기 때문에 파싱하기가 어렵다
        soup = BeautifulSoup(html, 'html.parser')
        price = soup.select_one("#_nowVal").text
        #print(price)  #아까 그 크롤링이 추출됨/. 이거는 콤마가 찍혀있어서 없애볼거임
        price = price.replace(',','')#대체한다 콤마를 공백으로
        price_all.append(price)
    return price_all

def  Day_of_the_week(): #날짜 제목
    day = ['월', '화', '수', '목', '금', '토', '일']
    Day_now = dt.datetime.today().weekday() #현재시각을 datetime객체로 반환 뒤 요일반환
    today = dt.datetime.now()
    return day, Day_now, today


#############################################시작
a = "Start News alarm"
notice_message(Token, "#kospi_notice", a,[]) # 시작한다는 알람 발송
print("start")
while True:
    try:
        now = dt.datetime.now()
        hour = str(now.hour)
        min = str(now.minute)
        if hour+min == "0900" or hour+min == "1500":
            print("send")
            title_list, href_list, img_list = bring_news() #함수 호출
            price_all = stock_code() # 주식가격호출
            day, Day_now, today = Day_of_the_week()
            TITLE =  f'{today.date()}-{day[Day_now]}요일' #메세지 제목
            attach_dict = { #슬랙에 보내는 형식
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"#삼성전자{price_all[0]}\n#SK하이닉스{price_all[1]}\n#LG에너지솔루션{price_all[2]}\n#삼성바이오로직스{price_all[3]}\n#LG화학{price_all[4]}\n"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "image",
                    "title": {
                        "type": "plain_text",
                        "text": "stock",
                        "emoji": True
                    },
                    "image_url": "https://ssl.pstatic.net/imgstock/chart3/day/KOSPI.png?sidcode=1632301488333",
                    "alt_text": "marg"
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "<{}|{}>".format(href_list[0],title_list[0])
                    },
                    "accessory": {
                        "type": "image",
                        "image_url": "{}".format(img_list[0]),
                        "alt_text": "cute cat"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "<{}|{}>".format(href_list[0], title_list[1])
                    },
                    "accessory": {
                        "type": "image",
                        "image_url": "{}".format(img_list[1]),
                        "alt_text": "cute cat"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "<{}|{}>".format(href_list[0], title_list[2])
                    },
                    "accessory": {
                        "type": "image",
                        "image_url": "{}".format(img_list[2]),
                        "alt_text": "cute cat"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "<{}|{}>".format(href_list[0], title_list[3])
                    },
                    "accessory": {
                        "type": "image",
                        "image_url": "{}".format(img_list[3]),
                        "alt_text": "cute cat"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "<{}|{}>".format(href_list[0], title_list[4])
                    },
                    "accessory": {
                        "type": "image",
                        "image_url": "{}".format(img_list[4]),
                        "alt_text": "cute cat"
                    }
                },
                {
                    "type": "divider"
                },
            ]
            }
            attach_list=[attach_dict] # 딕셔너리 형태를 리스트로 변환
            notice_message(Token, "#kospi_notice", TITLE, attach_list)
            time.sleep(60)
    except Exception as e:
        notice_message(Token, "#kospi_notice",e,[])
        time.sleep(60)