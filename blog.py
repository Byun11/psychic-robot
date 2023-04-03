from bs4 import BeautifulSoup
import requests
import pandas as pd
import time


def delete_iframe(url):
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "lxml") 

    src_url = "https://blog.naver.com/" + soup.iframe["src"]
    
    return src_url
# 본문 스크래핑
def text_scraping(url):
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "lxml") 

    if soup.find("div", attrs={"class":"se-main-container"}):
        text = soup.find("div", attrs={"class":"se-main-container"}).get_text()
        text = text.replace("\n","") #공백 제거
        return text
    else:
        return "확인불가"
    
def crawling():
    title_link = {"제목": [],"링크":[]}
    url='https://search.naver.com/search.naver?where=blog&query=%23%ED%98%91%EC%B0%AC&sm=tab_opt&nso=so%3Add%2Cp%3Aall'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    news_titles = soup.find_all("a", attrs={"class":"api_txt_lines total_tit"})
    
    for i in news_titles: #글 제목과 링크를 딕셔너리에 넣음
        title = i.get_text()
        href = i.attrs['href']
        title_link["제목"].append(title)
        title_link["링크"].append(href)
    
    title_link_df= pd.DataFrame(title_link) #데이터프레임화 
    #title_link_df= pd.DataFrame.from_dict(data=title_link, orient='index') #데이터프레임화 
    title_link_df["내용"] = 0
    for i in range(len(title_link_df.iloc[:,0])): #링크를 통해서 블로그 글 내용 긁어서 데이터 프레임에 넣음
        url=title_link_df.iloc[i,1]
        try:
            title_link_df.iloc[i,2] = text_scraping(delete_iframe(url))
        except:
            title_link_df.iloc[i,2] = None
    return title_link_df

#maincode
print("start")
title_link_df=crawling()
title_link_df.to_csv('title_link_df.csv')
while True:
    try:
        time.sleep(7200)
        title_link_df=crawling()
        read_blog=pd.read_csv('title_link_df.csv', index_col=0)
        todo_save=pd.concat([read_blog, title_link_df])
        todo_save.to_csv('title_link_df.csv')
    except:
        time.sleep(7200)