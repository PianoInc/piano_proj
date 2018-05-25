from bs4 import BeautifulSoup
from selenium import webdriver
import datetime
import re
import os
import sys
import time
sys.path.insert(0, 'e:\piano_proj\\venv\Scripts\piano_proj')
# Python이 실행될 때 DJANGO_SETTINGS_MODULE이라는 환경 변수에 현재 프로젝트의 settings.py파일 경로를 등록합니다.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "piano_proj.settings")
# 이제 장고를 가져와 장고 프로젝트를 사용할 수 있도록 환경을 만듭니다.
import django
from django.utils import timezone
django.setup()
from outsourcing_crawler.models import *
from rocket_bot.rocket_bot import send_to_marketing

#################################정규식#################################
p = re.compile("\d+")
week_p = re.compile("\d+주")
day_p = re.compile("\d+일")
hour_p = re.compile("\d+시간")
document_srl_p = re.compile("document_srl=\d+")
articleid_p = re.compile("articleid=\d+")
clubid_p = re.compile("clubid=\d+")
#################################정규식#################################
now = datetime.datetime.now()
now_date = now.strftime('%Y-%m-%d')

#due 기한이 얼마나 임박했는지 알려주자
RED_DF = 'red' #red     1주일 내
YEL_DF = 'yel' #yellow  2주일 내
DEF_DF = 'def' #default(White) 2주 이상

#Slack 공지 할것인지 안할것인지
INITIAL_CRAWLING = False
ADDITIONAL_CRAWLING = True
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
driver = webdriver.Chrome('e:\\chromedriver\\chromedriver.exe', chrome_options=chrome_options)
driver.implicitly_wait(3)

def make_due_use_date(due) :
    try :
        day = int(p.search(due).group())
    except :
        day = 0
    due_date = (now + datetime.timedelta(days=day)).strftime('%Y-%m-%d')
    return due_date

def get_last_id(data) :
    data_cnt = len(data)
    data_index = data_cnt - 1
    new_post = 0
    for n in range(data_cnt):
        if (len(data[data_index - n]['due']) == 10):
            if (now_date > data[data_index - n]['due']):  # due
                continue
        last_identifier = data[data_index - n]['identify']  # identifier
        print(last_identifier)
        return last_identifier

def update_due_flag():
    res = Jobs.objects.filter(vis=True).values()
    for biz in res :
        due_flag = check_date(biz['due'])
        print(due_flag)
        data = Jobs.objects.get(identify=biz['identify'])
        data.due_flag=due_flag
        data.save()

def read_data(site_name) :
    try:
        result = Jobs.objects.filter(site=site_name)
        if(len(result)) :
            return result.values()
    except:
        print("failed to read data!!")

def check_date(due_str):  # 기한의유효성을 확인.
    try :
        due = datetime.datetime.strptime(due_str, '%Y-%m-%d')
    except :
        print(due_str)
        return DEF_DF
    due_date = due.strftime('%Y-%m-%d')
    red_date = (now + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    yellow_date = (now + datetime.timedelta(days=14)).strftime('%Y-%m-%d')
    if due_date <= red_date:
        return RED_DF
    if due_date <= yellow_date:
        return YEL_DF
    return DEF_DF

def write_data(site, title, url, identifier, flag, price="게시물 참조", period="게시물 참조", due="게시물 참조", due_flag=DEF_DF) :
    try:
        #print(title, url, due, price, period, due_flag, identifier, site, datetime.datetime.now(), True, False)
        data = Jobs(title = title, url = url, due = due, price=price, period=period,due_flag=due_flag, identify = identifier, site = site, save_date = datetime.datetime.now(), vis = True,fav = False)
        if flag :
            msg = "%s에서 새로운 외주가 떳어요\n %s \n 링크는 여기! \n%s \n 기한은 %s 까지니까 서두르세요!\n Good Luck!\n" \
                  "------------------------------------------------------------------------------------------------------\n" % (site, title, url, due)
            send_to_marketing(msg)
        data.save()
    except:
        print("failed to save data!!")
        print(title, url, due, price, period, due_flag, identifier, site, datetime.datetime.now(), True, False)

def update_due_flag():
    res = Jobs.objects.filter(vis=True).values()
    for biz in res :
        due_flag = check_date(biz['due'])
        print(due_flag)
        data = Jobs.objects.get(identify=biz['identify'])
        data.due_flag=due_flag
        data.save()
################################################################################################
def wishket_make_due(due) :
    try :
        week = int(p.search(week_p.search(due).group()).group())
    except :
        week = 0
    try :
        day = int(p.search(day_p.search(due).group()).group())
    except :
        day = 0
    days = (week*7+day)
    due_date = (now + datetime.timedelta(days=days)).strftime('%Y-%m-%d')
    return due_date
def wishket_send_data(sections, flag) :
    BASE_URL = "https://www.wishket.com"
    for cnt in range(int(len(sections)/2)) :
        body = cnt*2
        head = body+1
        spans = sections[body].find_all('span')
        title = sections[head].find('a').text
        identifier = sections[head].find('a').get('href')
        url = BASE_URL + identifier
        price = spans[0].text
        period = spans[1].text
        due = wishket_make_due(spans[3].find('strong').text)
        due_flag = check_date(due)
        write_data("wishket", title, url, identifier, flag, price, period, due, due_flag)
    return False
def wishket_get_sections(html) :
    soup = BeautifulSoup(html, 'html.parser')
    lists = soup.find('div',{'class':'project-list-box'})
    sections = lists.find_all('section')
    return sections
def wishket() :
    LOGIN_URL = "https://www.wishket.com/accounts/login/"
    PROJ_URL = "https://www.wishket.com/project/"
    driver.get(PROJ_URL)
    driver.find_element_by_id('dev-2').click()
    time.sleep(3)

    all_sections = []
    end_flag = False
    data = read_data('wishket')
    if data :
        print("is data")
        last_identifier = get_last_id(data)
        while True :
            sections = wishket_get_sections(driver.page_source)
            for cnt in range(len(sections)) :
                spans = sections[cnt].find_all('span')
                identifier = sections[cnt].find('a').get('href')
                if identifier == last_identifier :
                    end_flag = True
                    break
                try :
                    due = wishket_make_due(spans[3].find('strong').text)
                except :
                    end_flag = True
                    break
                all_sections += sections[cnt]
            if end_flag :
                break
            driver.find_element_by_class_name('next').click()
            time.sleep(3)
        all_sections.reverse()
        wishket_send_data(all_sections, ADDITIONAL_CRAWLING)

    else :
        print("no data")
        while True :
            sections = wishket_get_sections(driver.page_source)
            for cnt in range(len(sections)) :
                spans = sections[cnt].find_all('span')
                try :
                    due = wishket_make_due(spans[3].find('strong').text)
                except :
                    end_flag = True
                    break
                all_sections += sections[cnt]
            if end_flag :
                break
            driver.find_element_by_class_name('next').click()
            time.sleep(3)
        all_sections.reverse()
        wishket_send_data(all_sections, INITIAL_CRAWLING)

def elancer_make_trs(html) :
    soup = BeautifulSoup(html, 'html.parser')
    lists = soup.find('table',{'class':'tb_st01'})
    trs = lists.find_all('tr')
    return trs

def elancer_send_data(trs, flag) :
    BASE_URL = "http://www.elancer.co.kr/02_HPJT/page/"
    for tr in trs :
        tds = tr.find_all('td')
        try :
            due = tr.find('td',{'class':'last'}).find('strong').text
        except :
            break
        if tds :
            title = tds[0].find('a').text
            identifier = tds[0].find('a').get('href')
            url = BASE_URL + identifier
            period = tds[2].text
            price = tds[4].text
            due = make_due_use_date(due)
            due_flag = check_date(due)
            write_data("elancer", title, url, identifier, flag, price, period, due, due_flag)
        else :
            break
def elancer() :
    PROJ_URL = "http://www.elancer.co.kr/02_HPJT/page/list.php?PCode=PCODE06#project_list"
    driver.get(PROJ_URL)
    time.sleep(3)

    all_trs = []
    end_flag = False
    data = read_data('elancer')

    page_cnt= 1
    new_job = 0
    if data :
        print("is data")
        last_identifier = get_last_id(data)
        trs = elancer_make_trs(driver.page_source)
        while True :
            for cnt in range(len(trs)) :
                tds = trs[cnt].find_all('td')
                if tds :
                    identifier = tds[0].find('a').get('href')
                    if identifier == last_identifier :
                        end_flag = True
                        break
                if trs[cnt].find('td') :
                    due = trs[cnt].find('td',{'class':'last'}).find('strong').text
                    if due == "모집완료" :
                        end_flag = True
                        break
            if end_flag :
                break
            new_job += 1
            try :
                driver.find_element_by_class_name('btn_lef').find_elements_by_tag_name('a')[page_cnt].click()
                page_cnt += 1
            except :
                break

        if new_job :
            all_trs = all_trs[:new_job]
        all_trs.reverse()
        elancer_send_data(all_trs,ADDITIONAL_CRAWLING)

    else :
        print("no data")
        while True :
            trs = elancer_make_trs(driver.page_source)
            for cnt in range(len(trs)) :
                if trs[cnt].find('td') :
                    due = trs[cnt].find('td',{'class':'last'}).find('strong').text
                    if due == "모집완료" :
                        print(cnt)
                        all_trs += trs[:cnt]
                        end_flag = True
                        break
            if end_flag :
                break
            all_trs += trs
            try :
                driver.find_element_by_class_name('btn_lef').find_elements_by_tag_name('a')[page_cnt].click()
                page_cnt += 1
            except :
                break
        print(all_trs)
        all_trs.reverse()
        elancer_send_data(all_trs,INITIAL_CRAWLING)

def freemoa_get_info_title(html) :
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find_all('div',{'class':'prjct-info-title'})
    return title
def freemoa_get_info_cont(html) :
    soup = BeautifulSoup(html, 'html.parser')
    container = soup.find_all('div',{'class':'prjct-info-container'})
    return container
def freemoa_send_data(info_title, info_cont, flag) :
    DETAIL_URL = "http://www.freemoa.net/m4/s41?page=1&sS="
    for cnt in range(len(info_cont)) :
        type = info_cont[cnt].find('span',{'class':'prjct-info-type-bold'}).text
        title = info_title[cnt].find('span',{'class':'ellipsis'}).text
        identifier = info_title[cnt].find('span',{'class':'ellipsis'}).get('data-pno')
        url = DETAIL_URL + title.replace('+','%2B',3)
        prj_info_l = info_cont[cnt].find('div',{'class':'prjct-info-left'}).find_all('li')
        price =  prj_info_l[0].find('div',{'class':'prjct-content'}).text
        period = prj_info_l[1].find('div',{'class':'prjct-content'}).text
        due = prj_info_l[2].find('div',{'class':'prjct-content'}).text
        due = make_due_use_date(due)
        due_flag = check_date(due)
        write_data('freemoa',title,url,identifier,flag,price,period,due,due_flag)
def freemoa() :
    n = 1
    PROJ_URL = "http://www.freemoa.net/m4/s41?f=1&page=%d"

    all_cont = []
    all_title = []
    end_flag = False
    data = read_data('freemoa')

    if data :
        print("is data")
        last_identifier = get_last_id(data)
        while True :
            driver.get(PROJ_URL % n)
            driver.execute_script("Project()")
            time.sleep(3)
            info_cont = freemoa_get_info_cont(driver.page_source)
            info_title = freemoa_get_info_title(driver.page_source)
            new_job = 0
            for cnt in range(len(info_title)) :
                identifier = info_title[cnt].find('span',{'class':'ellipsis'}).get('data-pno')
                if identifier == last_identifier :
                    end_flag = True
                    break
                state = info_title[cnt].find('div',{'class':'prjct-state'}).text
                if '마감' in state :
                    end_flag = True
                    break
                new_job += 1
            if new_job :
                all_cont += info_cont[:new_job]
                all_title += info_title[:new_job]
            if end_flag :
                break
            n += 1
        all_title.reverse()
        all_cont.reverse()
        freemoa_send_data(all_title,all_cont,ADDITIONAL_CRAWLING)

    else :
        print("no data")
        while True :
            driver.get(PROJ_URL % n)
            #자바스크립트를 실행시켜주어야....내용이보인다...으아아아아아아아으아아아아아아 망할놈의 동적사이트!
            driver.execute_script("Project()")
            time.sleep(3)
            info_cont = freemoa_get_info_cont(driver.page_source)
            info_title = freemoa_get_info_title(driver.page_source)
            new_job = 0
            for cnt in range(len(info_title)) :
                state = info_title[cnt].find('div',{'class':'prjct-state'}).text
                if '마감' in state :
                    end_flag = True
                    break
                new_job += 1
            if new_job :
                all_cont += info_cont[:new_job]
                all_title += info_title[:new_job]
            if end_flag :
                break
            n += 1
        all_title.reverse()
        all_cont.reverse()
        freemoa_send_data(all_title,all_cont,INITIAL_CRAWLING)
    return

def andpub_send_data(trs,flag) :
    for cnt in range(len(trs)) :
        tds = trs[cnt].find_all('td')
        if not tds :
            continue
        title = tds[2].find('a').text
        if '공지' in title :
            continue
        url = tds[2].find('a').get('href')
        identifier = document_srl_p.search(url).group()
        write_data('androidpub',title,url,identifier,flag)
def andpub_get_trs(html) :
    soup = BeautifulSoup(html, 'html.parser')
    lists = soup.find('table',{'class':'boardList'})
    trs = lists.find_all('tr')
    return trs
def androidpub() :
    PROJ_URL = "https://www.androidpub.com/index.php?mid=promotion&page=%d"

    all_trs = []
    end_flag = False
    data = read_data('androidpub')
    new_job = 0

    if data :
        print("is data")
        last_identifier = get_last_id(data)
        for n in range(5) :
            n += 1
            driver.get(PROJ_URL % n)
            trs = andpub_get_trs(driver.page_source)
            new_job = 0
            for cnt in range(len(trs)) :
                tds = trs[cnt].find_all('td')
                if not tds :
                    continue
                identifier = document_srl_p.search(tds[2].find('a').get('href')).group()
                if identifier == last_identifier :
                    end_flag = True
                    break
                new_job += 1
            if end_flag :
                break
        if new_job :
            all_trs = trs[:new_job]
        all_trs.reverse()
        andpub_send_data(all_trs,ADDITIONAL_CRAWLING)
    else :
        print("no data")
        for n in range(5) :
            n += 1
            driver.get(PROJ_URL % n)
            trs = andpub_get_trs(driver.page_source)
            all_trs += trs
        all_trs.reverse()
        andpub_send_data(all_trs,INITIAL_CRAWLING)
    return

def cafe_send_data(site, spans, flag) :
    BASE_URL = "cafe.naver.com"
    for cnt in range(len(spans)) :
        title = spans[cnt].find('a').text
        url = BASE_URL + spans[cnt].find('a').get('href')
        clubid = clubid_p.search(url).group()
        articleid = articleid_p.search(url).group()
        identifier = clubid+"&"+articleid
        write_data(site, title, url, identifier, flag)

def cafe_get_spans(html) :
    soup = BeautifulSoup(html, 'html.parser')
    form = soup.find('form',{'name':'ArticleList'})
    spans = form.find_all('span',{'class':'aaa'})
    return spans

def oejunara() :
    PROJ_URL = "http://cafe.naver.com/ArticleList.nhn?&search.menuid=13&search.boardtype=L&search.questionTab=A&search.totalCount=151&search.clubid=24657232&search.page=%d"

    all_spans = []
    end_flag = False
    data = read_data('oejunara')
    new_job = 0
    if data :
        print("is data")
        last_identifier = get_last_id(data)
        for page in range(3) :
            page += 1
            driver.get(PROJ_URL % page)
            driver.switch_to_frame('cafe_main')
            spans = cafe_get_spans(driver.page_source)
            new_job = 0
            for cnt in range(len(spans)) :

                clubid = clubid_p.search(spans[cnt].find('a').get('href')).group()
                articleid = articleid_p.search(spans[cnt].find('a').get('href')).group()
                identifier = clubid+"&"+articleid
                if identifier == last_identifier :
                    end_flag = True
                    break
                new_job += 1
            if end_flag :
                break
        if new_job :
            all_spans  = spans[:new_job]
        all_spans.reverse()
        cafe_send_data('oejunara', all_spans, ADDITIONAL_CRAWLING)
    else :
        print("no data")
        for page in range(1) :
            page += 1
            driver.get(PROJ_URL % page)
            driver.switch_to_frame('cafe_main')
            spans = cafe_get_spans(driver.page_source)
            all_spans += spans
        all_spans.reverse()
        cafe_send_data('oejunara', all_spans,INITIAL_CRAWLING)
    return

def macbugi() :
    PROJ_URL = "http://cafe.naver.com/ArticleList.nhn?search.clubid=16914752&search.menuid=28&search.boardtype=L&search.page=%d"

    all_spans = []
    end_flag = False
    data = read_data('macbugi')
    new_job = 0
    if data :
        print("is data")
        last_identifier = get_last_id(data)
        for page in range(3) :
            page += 1
            driver.get(PROJ_URL % page)
            driver.switch_to_frame('cafe_main')
            spans = cafe_get_spans(driver.page_source)
            new_job = 0
            for cnt in range(len(spans)) :

                clubid = clubid_p.search(spans[cnt].find('a').get('href')).group()
                articleid = articleid_p.search(spans[cnt].find('a').get('href')).group()
                identifier = clubid+"&"+articleid
                if identifier == last_identifier :
                    end_flag = True
                    break
                new_job += 1
            if end_flag :
                break
        if new_job :
            all_spans  = spans[:new_job]
        all_spans.reverse()
        cafe_send_data('macbugi', all_spans, ADDITIONAL_CRAWLING)
    else :
        print("no data")
        for page in range(1) :
            page += 1
            driver.get(PROJ_URL % page)
            driver.switch_to_frame('cafe_main')
            spans = cafe_get_spans(driver.page_source)
            all_spans += spans
        all_spans.reverse()
        cafe_send_data('macbugi', all_spans,INITIAL_CRAWLING)
    return
"""
driver.get(LOGIN_URL)
driver.find_element_by_id('id_identification').send_keys('rlatnfh99')
driver.find_element_by_id('id_password').send_keys('sephora88')
driver.find_element_by_class_name('btn-lg').click()
"""
def main() :
    wishket()
    elancer()
    freemoa()
    androidpub()
    oejunara()
    macbugi()
    update_due_flag()

main()
driver.close()
