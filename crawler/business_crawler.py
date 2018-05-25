from bs4 import BeautifulSoup
import datetime
import requests
import re
import os
import sys
sys.path.insert(0, 'e:\piano_proj\\venv\Scripts\piano_proj')
# Python이 실행될 때 DJANGO_SETTINGS_MODULE이라는 환경 변수에 현재 프로젝트의 settings.py파일 경로를 등록합니다.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "piano_proj.settings")
# 이제 장고를 가져와 장고 프로젝트를 사용할 수 있도록 환경을 만듭니다.
import django
from django.utils import timezone
django.setup()

from money_crawler.models import *
from rocket_bot.rocket_bot import send_to_marketing

now = datetime.datetime.now()
now_date = now.strftime('%Y-%m-%d')

#Slack 공지 할것인지 안할것인지
INITIAL_CRAWLING = False
ADDITIONAL_CRAWLING = True

#due 기한이 얼마나 임박했는지 알려주자
RED_DF = 'red' #red     1주일 내
YEL_DF = 'yel' #yellow  2주일 내
DEF_DF = 'def' #default(White) 2주 이상

###########################################정규식###########################################
p = re.compile('\d+')
# egbiz identify 추출 정규식
id_p = re.compile('\w\w\d{12}')
# egbiz date 추출 정규식
date_p = re.compile('\d{4}-\d{2}-\d{2}')

###K-startup 정규식
searchPostSn_p = re.compile('\d{5}')
bi_postSeq_p = re.compile('\d{9}')

###ripc 정규식
notice_seq_p = re.compile('\d{4}')
notice_status_p = re.compile('NO\d{3}')
year_p = re.compile('\d{4}')

#nipa 정규식
last_page_p = re.compile('page=\d+')

#nipa 정규식
last_page_p = re.compile('page=\d+')

#kocca 정규식
pageIndex_p = re.compile('pageIndex=\d+')
intcNo_p = re.compile('intcNo=\d+\w+\d+')

#kipa 정규식
article_no_p = re.compile('mode=view&article_no=\d+')
pager_offset_p = re.compile('offset=\d+')

#kdb 정규식
dbnum_p = re.compile('dbnum=\d+')
page_p = re.compile('page=\d+')

#gbsa 정규식
value_p = re.compile("value=\d+")
annc_no_p = re.compile('\d{8}')
###########################################정규식###########################################
def read_data(site_name) :
    try:
        result = Business.objects.filter(site=site_name)
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

def write_data(site_name, name, url, due, due_flag, identifier, flag) :
    try:
        data = Business(title = name, url = url, due = due,due_flag=due_flag, identify = identifier, site = site_name, save_date = datetime.datetime.now(), vis = True,fav = False)
        #print(name, url, due, due_flag, identifier, site_name,  datetime.datetime.now(),  True, False)
        if flag :
            msg = "%s에서 새로운 공고가 떳어요\n %s \n 링크는 여기! \n%s \n 기한은 %s 까지니까 서두르세요!\n Good Luck!\n------------------------------------------------------------------------------------------------------\n" % (site_name, name, url, due)
            send_to_marketing(msg)
        data.save()
    except:
        print("failed to save data!!")

def invis_past_biz():
    data = Business.objects.filter(vis=True).values()
    if(data) :
        data_cnt = len(data)
        for n in range(data_cnt):
            if len(data[n]['due']) == 10 :
                try :
                    due = datetime.strptime(data[n]['due'], '%Y-%m-%d')
                except :
                    continue
                due_date = due.strftime('%Y-%m-%d')
                if now_date > due_date:
                    res = Business.objects.get(identify=data[n]['identify'])
                    res.vis = False
                    res.fav = False
                    while True :
                        try :
                            res.save()
                            print("save", due)
                            break
                        except :
                            print("retry")

            if data[n]['due'] == "마감" :
                res = Business.objects.get(identify=data[n]['identify'])
                res.vis = False
                res.fav = False
                while True :
                    try :
                        res.save()
                        break
                    except :
                        print("retry")

def update_due_flag():
    res = Business.objects.filter(vis=True).values()
    for biz in res :
        due_flag = check_date(biz['due'])
        print(due_flag)
        data = Business.objects.get(identify=biz['identify'])
        data.due_flag=due_flag
        data.save()


def bizinfo_send_data(all_trs, flag):
    # 글의 기본 URL이다.
    BASE_URL = "http://www.bizinfo.go.kr/see/seea/selectSEEA140Detail.do?pblancId=%s&menuId=80001001001"

    for tr_cnt in range(len(all_trs)) :
        # 첫번째 td에서 글번호
        tds = all_trs[tr_cnt].find_all("td")
        num = tds[0].string.lstrip().rstrip().replace(",", "")
        due_ori = tds[2].string.lstrip().rstrip()
        if len(due_ori) == 23:
            due_ori = due_ori[13:]
        due_flag = check_date(due_ori)
        name = all_trs[tr_cnt].find("a").text.lstrip().rstrip()
        identifier = all_trs[tr_cnt].find("a").get('onclick')[17:37]
        url = BASE_URL % identifier
        while 1 :
            try :
                write_data('bizinfo', name, url, due_ori, due_flag, identifier, flag)
                break
            except :
                print("Write error")
def bizinfo():

    # Page를 변경할 변수를 선언한다.
    page = 1
    # while을 종료할수있는 플래그를 만든다.
    end_flag = False

    data = read_data("bizinfo")
    if(data) :
        data_cnt = len(data)
        data_index = data_cnt - 1
        new_post = 0
        for n in range(data_cnt):
            if (len(data[data_index - n]['due']) == 10):
                if (now_date > data[data_index - n]['due']):  # due
                    continue
            last_identifier = data[data_index - n]['identify']  # identifier
            break

        all_trs = []
        while 1:
            if end_flag:
                break
            # 순차적으로 다음페이지에 접속하기 위해 URL을 만들어준다.
            INPUT_URL = "http://www.bizinfo.go.kr/see/seea/selectSEEA100.do?pageIndex=%d" % page
            # Page 변경후 i값을 1 증가시켜 다음 페이지를 열 준비를 한다.
            page = page + 1
            # 홈페이지에 접속한다.
            req = requests.get(INPUT_URL)
            # 페이지의 element 모두가져오기
            html_parse = req.text
            soup = BeautifulSoup(html_parse, 'html.parser')
            trs = soup.select("#content > div.boardBusiness > div.bbsTable > table > tbody > tr")
            if len(trs) == 1:
                break
            all_trs += trs
            for tr_cnt in range(len(trs)):
                identifier = trs[tr_cnt].find("a").get('onclick')[17:37]
                if(identifier == last_identifier) :
                    end_flag = 1
                    break
                new_post += 1
        if(new_post) :
            all_trs = all_trs[:new_post]
            all_trs.reverse()
            bizinfo_send_data(all_trs, ADDITIONAL_CRAWLING)

    else:
        all_trs = []
        while 1:
            if end_flag:
                break
            # 순차적으로 다음페이지에 접속하기 위해 URL을 만들어준다.
            INPUT_URL = "http://www.bizinfo.go.kr/see/seea/selectSEEA100.do?pageIndex=%d" % page
            page = page + 1
            # 홈페이지에 접속한다.
            req = requests.get(INPUT_URL)
            # 페이지의 element 모두가져오기
            html_parse = req.text
            soup = BeautifulSoup(html_parse, 'html.parser')

            trs = soup.select("#content > div.boardBusiness > div.bbsTable > table > tbody > tr")
            if len(trs) == 1:
                break
            all_trs += trs

        all_trs.reverse()
        bizinfo_send_data(all_trs, INITIAL_CRAWLING)
        return


def kstartup_send_data(titles, top_list_cnt, uls, flag):
    BASE_URL = "http://k-startup.go.kr/common/announcement/announcementDetail.do?searchDtlAncmSn=0&searchPrefixCode=BOARD_701_001&searchBuclCd=&searchAncmId=&searchPostSn=%s&bid=701&mid=30004&searchBusinessSn=0"
    BASE_BI_URL = "http://bi.go.kr/board/editViewPop.do?boardID=RECRUIT&postSeq=%s"
    for title_cnt in range(len(titles) - top_list_cnt):
        name = titles[title_cnt].text.lstrip().rstrip()
        lis = uls[title_cnt].find_all("li")
        if len(lis) > 2:
            due_ori = lis[2].text.lstrip().rstrip()[6:16]
        else:
            due_ori = "공고참조"
        due_flag = check_date(due_ori)
        # 글의 HREF값을 가져옴
        href = titles[title_cnt].get('href')
        if href.find('itemSelect') >= 0:
            identifier = searchPostSn_p.search(href).group()
            url = BASE_URL % identifier
        if href.find('biNetSelect') >= 0:
            identifier = bi_postSeq_p.search(href).group()
            url = BASE_BI_URL % identifier
        while True :
            try :
                write_data('kstartup', name, url, due_ori, due_flag, identifier, flag)
                break
            except :
                print("Write error")
def kstratup():
    # 페이지에 접속하기 위해 URL을 만들어준다.
    INPUT_URL = "https://www.k-startup.go.kr/common/announcement/announcementList.do?mid=30004&bid=701"

    data = read_data("kstartup")

    if data:
        print("is data")
        data_cnt = len(data)
        data_index = data_cnt - 1
        new_post = 0

        for n in range(data_cnt):
            if (len(data[data_index - n]['due']) == 10):
                if (now_date > data[data_index - n]['due']):  # due
                    continue
            last_identifier = data[data_index - n]['identify']  # identifier
            print(last_identifier)
            break
        end_flag = 0
        while 1:
            if end_flag:
                break
                # 홈페이지에 접속한다.
            req = requests.get(INPUT_URL)
            # 페이지의 element 모두가져오기
            html_parse = req.text
            soup = BeautifulSoup(html_parse, 'html.parser')
            # 사업명이 들어있는 필드에 접근해서 모든 사업명을 total_title이라는 변수에 넣는답
            listwrap = soup.find_all(class_="listwrap")
            # 공지 갯수
            top_list_cnt = len(listwrap[0].find_all(class_="list_info"))
            titles = soup.select("#content_w1100 > div.listwrap > ul > li > h4 > a")[top_list_cnt:]

            for title_cnt in range(len(titles)):
                href = titles[title_cnt].get('href')
                if href.find('itemSelect') >= 0:
                    identifier = searchPostSn_p.search(href).group()
                if href.find('biNetSelect') >= 0:
                    identifier = bi_postSeq_p.search(href).group()
                if (identifier == last_identifier):
                    end_flag = 1
                    break
                new_post += 1

        if new_post:
            titles = titles[:new_post]
            titles.reverse()
            uls = soup.select("#content_w1100 > div.listwrap > ul > li > ul")[:new_post]
            uls.reverse()
            kstartup_send_data(titles, top_list_cnt, uls, ADDITIONAL_CRAWLING)

    else :
        print("no data")
        # 홈페이지에 접속한다.
        req = requests.get(INPUT_URL)
        # 페이지의 element 모두가져오기
        html_parse = req.text
        soup = BeautifulSoup(html_parse, 'html.parser')
        # 사업명이 들어있는 필드에 접근해서 모든 사업명을 total_title이라는 변수에 넣는답
        titles = soup.select("#content_w1100 > div.listwrap > ul > li > h4 > a")
        titles.reverse()
        listwrap = soup.find_all(class_="listwrap")

        # 공지 갯수
        top_list_cnt = len(listwrap[0].find_all(class_="list_info"))
        uls = soup.select("#content_w1100 > div.listwrap > ul > li > ul")
        uls.reverse()
        kstartup_send_data(titles, top_list_cnt, uls, INITIAL_CRAWLING)


def snventure_send_data(all_trs, flag):
    BASE_URL = "http://www.snventure.net/vnet/fe/snv/gonggo/%s"

    for tr_cnt in range(len(all_trs)):
        tds = all_trs[tr_cnt].find_all("td")
        due_ori = tds[2].string.lstrip().rstrip()
        due_flag = check_date(due_ori)
        name = all_trs[tr_cnt].find("a").text.lstrip().rstrip()
        identifier = all_trs[tr_cnt].find("a").get('href').replace("¤", "&")
        url = BASE_URL % identifier
        while 1 :
            try :
                write_data('snventure', name, url, due_ori, due_flag, identifier, flag)
                break
            except :
                print("Write error")
def snventure():
    # while을 종료할수있는 플래그를 만든다.
    end_flag = False
    all_trs = []
    data = read_data("snventure")
    page = 1
    if(data):
        data_cnt = len(data)
        data_index = data_cnt - 1
        new_post = 0

        for n in range(data_cnt):
            if (len(data[data_index - n]['due']) == 10):
                if (now_date > data[data_index - n]['due']):  # due
                    continue
            last_identifier = data[data_index - n]['identify']  # identifier
            print(last_identifier)
            break
        while 1:
            if end_flag:
                break

            INPUT_URL = "http://www.snventure.net/vnet/fe/snv/gonggo/NR_list.do?snp=&menuNo=19&currentPage=%d&rowPerPage=10&searchKey=&searchVal=" % page
            page = page + 1
            req = requests.get(INPUT_URL)
            # 페이지의 element 모두가져오기
            html_parse = req.text
            soup = BeautifulSoup(html_parse, 'html.parser')
            # 사업명이 들어있는 필드에 접근해서 모든 사업명을 total_title이라는 변수에 넣는답
            is_nodata = soup.find(class_="no-data")
            if is_nodata:
                break
            ntc_cnt = len(soup.find(class_="ntc"))
            trs = soup.select("#contents > table > tbody > tr")[ntc_cnt:]

            all_trs += trs
            for tr_cnt in range(len(trs)):
                identifier = trs[tr_cnt].find("a").get('href').replace("¤", "&")
                if(identifier == last_identifier) :
                    end_flag = 1
                    break
                new_post += 1
        if(new_post):
            all_trs = all_trs[:new_post]
            all_trs.reverse()
            snventure_send_data(all_trs, ADDITIONAL_CRAWLING)
    else :
        while 1:
            INPUT_URL = "http://www.snventure.net/vnet/fe/snv/gonggo/NR_list.do?snp=&menuNo=19&currentPage=%d&rowPerPage=10&searchKey=&searchVal=" % page
            page = page + 1
            req = requests.get(INPUT_URL)
            # 페이지의 element 모두가져오기
            html_parse = req.text
            soup = BeautifulSoup(html_parse, 'html.parser')
            # 사업명이 들어있는 필드에 접근해서 모든 사업명을 total_title이라는 변수에 넣는답
            is_nodata = soup.find(class_="no-data")
            if is_nodata:
                break
            ntc_cnt = len(soup.find(class_="ntc"))
            trs = soup.select("#contents > table > tbody > tr")[ntc_cnt:]
            all_trs += trs
        all_trs.reverse()
        snventure_send_data(all_trs, INITIAL_CRAWLING)


def smtech_send_data(all_trs, flag):
    # 글의 기본 URL이다.
    BASE_URL = "http://www.smtech.go.kr%s"

    for tr_cnt in range(len(all_trs)):
        # 첫번째 td에서 글번호
        tds = all_trs[tr_cnt].find_all("td")
        due_ori = tds[3].find("div").string.lstrip().rstrip()[16:28].replace(". ", "-", 2)
        due_flag = check_date(due_ori)
        name = all_trs[tr_cnt].find("a").text.lstrip().rstrip()
        identifier = all_trs[tr_cnt].find("a").get('href')[:32]+all_trs[tr_cnt].find("a").get('href')[131:]
        url = BASE_URL % identifier
        while True:
            try:
                write_data('smtech', name, url, due_ori, due_flag, identifier, flag)
                break
            except:
                print("write error")
def smtech():
    # Page를 변경할 변수를 선언한다.
    page = 1
    # while을 종료할수있는 플래그를 만든다.
    end_flag = False
    all_trs = []
    data = read_data("smtech")
    if(data):
        print("is data")
        data_cnt = len(data)
        data_index = data_cnt - 1
        new_post = 0

        for n in range(data_cnt):
            if (len(data[data_index - n]['due']) == 10):
                if (now_date > data[data_index - n]['due']):  # due
                    continue
            last_identifier = data[data_index - n]['identify']  # identifier
            print(last_identifier)
            break

        while 1:
            if end_flag:
                break
            INPUT_URL = "http://www.smtech.go.kr/front/ifg/no/notice02_list.do?pageIndex=%d" % page
            page = page + 1
            req = requests.get(INPUT_URL)
            # 페이지의 element 모두가져오기
            html_parse = req.text
            soup = BeautifulSoup(html_parse, 'html.parser')
            # 사업명이 들어있는 필드에 접근해서 모든 사업명을 total_title이    라는 변수에 넣는답
            trs = soup.select("#subcontent > div.right > div.l15 > div.t20 > table.tbl_type01 > tbody > tr")
            all_trs += trs
            for tr_cnt in range(len(trs)):
                identifier = trs[tr_cnt].find("a").get('href')[:32]+trs[tr_cnt].find("a").get('href')[131:]
                if (identifier == last_identifier):
                    end_flag = 1
                    break
                new_post += 1
        if (new_post):
            all_trs = all_trs[:new_post]
            all_trs.reverse()
            smtech_send_data(all_trs, ADDITIONAL_CRAWLING)

    else :
        print("no data")
        while 1:
            print(page)
            INPUT_URL = "http://www.smtech.go.kr/front/ifg/no/notice02_list.do?pageIndex=%d" % page
            page = page + 1

            req = requests.get(INPUT_URL)
            # 페이지의 element 모두가져오기
            html_parse = req.text
            soup = BeautifulSoup(html_parse, 'html.parser')
            # 사업명이 들어있는 필드에 접근해서 모든 사업명을 total_title이    라는 변수에 넣는답
            trs = soup.select("#subcontent > div.right > div.l15 > div.t20 > table.tbl_type01 > tbody > tr")

            if len(trs) == 1:
                print(trs[0].find('td').text)
                break
            all_trs += trs
        all_trs.reverse()
        smtech_send_data(all_trs, INITIAL_CRAWLING)


def ripc_send_data(all_trs, flag):
    HREF_SRC = "/online/csDetail.do?notice_seq=%s&notice_status_code=%s"
    BASE_URL = "https://biz.ripc.org%s"
    for tr_cnt in range(len(all_trs)):
        tds = all_trs[tr_cnt].find_all("td")
        if tds[0].text == "지원사업 공고가 없습니다.":
            continue
        due_ori = now_date[:4] + "-" + tds[3].text[6:].replace(".", "-")
        due_flag = check_date(due_ori)
        title = all_trs[tr_cnt].find("a")
        name = title.text.lstrip().rstrip()

        notice_seq = notice_seq_p.search(title.get('href')).group()
        notice_status_code = notice_status_p.search(title.get('href')).group()

        identifier = HREF_SRC % (notice_seq, notice_status_code)
        url = BASE_URL % identifier
        while (1):
            try:
                write_data('ripc', name, url, due_ori, due_flag, identifier, flag)
                break
            except:
                print("Write error")
def ripc():
    HREF_SRC = "/online/csDetail.do?notice_seq=%s&notice_status_code=%s"
    # page를 변경할 변수를 선언한다.
    page = 1
    # while을 종료할수있는 플래그를 만든다.
    end_flag = False
    all_trs = []
    # 몇개를 발견했는지 세보자
    cnt = 1
    data = read_data("ripc")

    INPUT_URL = "https://biz.ripc.org/online/csNotice.do?pageNum=%d"

    #마지막 페이지 넘버 가져오기
    req = requests.get(INPUT_URL % page, verify=False)  # verify를 false를 주지않으면 받아오질 못함; ssl오류남;
    # 페이지의 element 모두가져오기
    html_parse = req.text
    soup = BeautifulSoup(html_parse, 'html.parser')
    lis = soup.select("#noticeForm > dl.right > dd > div.align_c > ul.pagination > li")
    last_li = lis[len(lis)-1]
    last_page_href = last_li.find('a').get('href')
    last_page_cnt = int(p.search(last_page_href).group())

    if (data):
        print("is data")
        data_cnt = len(data)
        data_index = data_cnt - 1
        new_post = 0

        for n in range(data_cnt):
            if (len(data[data_index - n]['due']) == 10):
                if now_date > data[data_index - n]['due']:  # due
                    continue
            last_identifier = data[data_index - n]['identify']  # identifier
            print(n, last_identifier)
            break

        for page in range(last_page_cnt):
            page = page + 1
            if end_flag:
                break
            input_url = INPUT_URL % page
            req = requests.get(input_url, verify=False)  # verify를 False를 주지않으면 받아오질 못함; SSL오류남;
            # 페이지의 element 모두가져오기
            html_parse = req.text
            soup = BeautifulSoup(html_parse, 'html.parser')
            # 사업명이 들어있는 필드에 접근해서 모든 사업명을 total_title이    라는 변수에 넣는답
            trs = soup.select("#noticeForm > dl > dd > table > tbody > tr")
            all_trs += trs
            for tr_cnt in range(len(trs)):
                title = all_trs[tr_cnt].find("a")

                #todo 정규표현식으로 변경하기
                notice_seq = notice_seq_p.search(title.get('href')).group()
                notice_status_code = notice_status_p.search(title.get('href')).group()

                identifier = HREF_SRC % (notice_seq, notice_status_code)
                print(identifier)
                if (identifier == last_identifier):
                    end_flag = True
                    break
                new_post += 1
        if (new_post):
            all_trs = all_trs[:new_post]
            all_trs.reverse()
            print(new_post)
            ripc_send_data(all_trs, ADDITIONAL_CRAWLING)
    else:
        print("no data")
        for page in range(last_page_cnt):
            page = page + 1
            if end_flag:
                break

            input_url = INPUT_URL % page
            req = requests.get(input_url, verify=False)  # verify를 false를 주지않으면 받아오질 못함; ssl오류남;
            # 페이지의 element 모두가져오기
            html_parse = req.text
            soup = BeautifulSoup(html_parse, 'html.parser')
            # 사업명이 들어있는 필드에 접근해서 모든 사업명을 total_title이    라는 변수에 넣는답
            trs = soup.select("#noticeForm > dl > dd > table > tbody > tr")
            all_trs += trs
        all_trs.reverse()
        ripc_send_data(all_trs, INITIAL_CRAWLING)
    return

def egbiz_send_data(trs, flag):
    BASE_URL ="https://www.egbiz.or.kr/prjCategory/a/m/selectPrjView.do?prjDegreeId=%s"
    for tr_cnt in range(len(trs)):
        tds = trs[tr_cnt].find_all("td")
        if 'tablebottom' in tds[0].get("class") :
            continue

        if tds[3].text.lstrip().rstrip() == "추후공지":
            due_ori = tds[3].text.lstrip().rstrip()
        else :
            due_ori = date_p.findall(tds[3].text.lstrip().rstrip())[1]

        due_flag = check_date(due_ori)
        title = trs[tr_cnt].find("a")
        name = title.text.lstrip().rstrip()
        identifier = id_p.search(title.get("onclick")).group()

        url = BASE_URL % identifier
        while (1):
            try:
                write_data('egbiz_a', name, url, due_ori, due_flag, identifier, flag)
                break
            except:
                print("Write error")
def egbiz():
    # 글의 기본 url이다.
    BASE_URL ="https://www.egbiz.or.kr/prjCategory/a/m/selectPrjView.do?prjDegreeId=%s"

    # page를 변경할 변수를 선언한다.
    page = 1
    # while을 종료할수있는 플래그를 만든다.
    end_flag = False
    all_trs = []
    data = read_data("egbiz_a")

    INPUT_URL = "https://www.egbiz.or.kr/prjCategory/a/m/selectPrjCategoryList.do?pageIndex=%d"

    req = requests.get(INPUT_URL % page, verify=False)  # verify를 false를 주지않으면 받아오질 못함; ssl오류남;
    # 페이지의 element 모두가져오기
    html_parse = req.text
    soup = BeautifulSoup(html_parse, 'html.parser')

    try :
        last_page_cnt = int(p.search(soup.find("form", {"id":"listForm"}).find("p", {"class":"paging"}).find_all("span", {"class":"selectPage"})[1].find_all("a")[1].get("onclick")).group())
    except :
        last_page_cnt = len(soup.find("form", {"id":"listForm"}).find("p", {"class":"paging"}).find_all("a")[-1].string)

    if data:
        print("is data")
        data_cnt = len(data)
        data_index = data_cnt - 1
        new_post = 0

        for n in range(data_cnt):
            if (len(data[data_index - n]['due']) == 10):
                if (now_date > data[data_index - n]['due']):  # due
                    continue
            last_identifier = data[data_index - n]['identify']  # identifier
            print(last_identifier)
            break

        for page in range(last_page_cnt):
            page = page + 1

            if end_flag:
                break
            input_url = INPUT_URL % page
            req = requests.get(input_url, verify=False)  # verify를 False를 주지않으면 받아오질 못함; SSL오류남;
            # 페이지의 element 모두가져오기
            html_parse = req.text
            soup = BeautifulSoup(html_parse, 'html.parser')
            # 사업명이 들어있는 필드에 접근해서 모든 사업명을 total_title이    라는 변수에 넣는답
            trs = soup.find("table", {"class":"subChart1-1"}).find("tbody", {"id":"mainBoardList"}).find_all("tr")

            all_trs += trs
            for tr_cnt in range(len(trs)):
                tds = trs[tr_cnt].find_all("td")
                if 'tablebottom' in tds[0].get("class") :
                    print("right")
                    continue
                title = trs[tr_cnt].find("a")
                identifier = id_p.search(title.get("onclick")).group()
                if (identifier == last_identifier):
                    end_flag = True
                    break
                new_post += 1
        if (new_post):
            all_trs = all_trs[:new_post]
            all_trs.reverse()
            egbiz_send_data(all_trs, ADDITIONAL_CRAWLING)
    else:
        print("no data")
        for page in range(last_page_cnt):
            page = page + 1
            if end_flag:
                break

            input_url = INPUT_URL % page
            req = requests.get(input_url, verify=False)  # verify를 false를 주지않으면 받아오질 못함; ssl오류남;
            # 페이지의 element 모두가져오기
            html_parse = req.text
            soup = BeautifulSoup(html_parse, 'html.parser')
            # 사업명이 들어있는 필드에 접근해서 모든 사업명을 total_title이    라는 변수에 넣는답
            trs = soup.find("table", {"class":"subChart1-1"}).find("tbody", {"id":"mainBoardList"}).find_all("tr")
            all_trs += trs
        all_trs.reverse()
        egbiz_send_data(all_trs, INITIAL_CRAWLING)
    return


def nipa_send_data(trs, flag):
    BASE_URL ="http://www.nipa.kr/biz/%s"
    for tr_cnt in range(len(trs)):
        tds = trs[tr_cnt].find_all("td")
        due_ori = "공고참조"
        due_flag = check_date(due_ori)
        title = trs[tr_cnt].find("a")
        name = title.text.lstrip().rstrip()
        identifier = title.get("onclick")[13:-5]
        url = BASE_URL % identifier
        while (1):
            try:
                #print('nipa', name, url, due_ori, due_flag, identifier, flag)
                write_data('nipa', name, url, due_ori, due_flag, identifier, flag)
                break
            except:
                print("Write error")
def nipa():
    # 글의 기본 url이다.
    BASE_URL ="http://www.nipa.kr/biz/%s"

    # page를 변경할 변수를 선언한다.
    page = 1
    # while을 종료할수있는 플래그를 만든다.
    end_flag = False
    all_trs = []
    data = read_data("nipa")

    INPUT_URL = "http://www.nipa.kr/biz/bizNotice.it?sortOrder=DESC&sort=registDate&pageSize=10&boardId=info&menuNo=18&page=%d"

    req = requests.get(INPUT_URL % page, verify=False)  # verify를 false를 주지않으면 받아오질 못함; ssl오류남;
    # 페이지의 element 모두가져오기
    html_parse = req.text
    soup = BeautifulSoup(html_parse, 'html.parser')

    try :
        last_page_cnt = int(p.search(last_page_p.search(soup.find("div", {"class":"pagination"}).find("a", {"class":"nextEnd"}).get("onclick")).group()).group())
    except :
        last_page_cnt = len(p.search(last_page_p.search(soup.find("div", {"class":"pagination"}).find_all("a")[-1].get("onclick")).group()).group())

    if data:
        print("is data")
        data_cnt = len(data)
        data_index = data_cnt - 1
        new_post = 0

        for n in range(data_cnt):
            if (len(data[data_index - n]['due']) == 10):
                if (now_date > data[data_index - n]['due']):  # due
                    continue
            last_identifier = data[data_index - n]['identify']  # identifier
            print(last_identifier)
            break

        for page in range(last_page_cnt):
            page = page + 1

            if end_flag:
                break
            input_url = INPUT_URL % page
            req = requests.get(input_url, verify=False)  # verify를 False를 주지않으면 받아오질 못함; SSL오류남;
            # 페이지의 element 모두가져오기
            html_parse = req.text
            soup = BeautifulSoup(html_parse, 'html.parser')
            # 사업명이 들어있는 필드에 접근해서 모든 사업명을 total_title이    라는 변수에 넣는답
            trs = soup.find("table", {"class":"boardList"}).find("tbody").find_all("tr")

            all_trs += trs
            for tr_cnt in range(len(trs)):
                title = trs[tr_cnt].find("a")
                identifier = title.get("onclick")[13:-5]
                if (identifier == last_identifier):
                    end_flag = True
                    break
                new_post += 1
        if (new_post):
            all_trs = all_trs[:new_post]
            all_trs.reverse()
            nipa_send_data(all_trs, ADDITIONAL_CRAWLING)
    else:
        print("no data")
        for page in range(last_page_cnt):
            page = page + 1
            if end_flag:
                break

            input_url = INPUT_URL % page
            req = requests.get(input_url, verify=False)  # verify를 false를 주지않으면 받아오질 못함; ssl오류남;
            # 페이지의 element 모두가져오기
            html_parse = req.text
            soup = BeautifulSoup(html_parse, 'html.parser')
            # 사업명이 들어있는 필드에 접근해서 모든 사업명을 total_title이    라는 변수에 넣는답
            trs = soup.find("table", {"class":"boardList"}).find("tbody").find_all("tr")
            all_trs += trs
        all_trs.reverse()
        nipa_send_data(all_trs, INITIAL_CRAWLING)
    return


def kocca_send_data(trs, flag):
    BASE_URL ="http://www.kocca.kr/cop/pims/view.do?%s"
    for tr_cnt in range(len(trs)):
        tds = trs[tr_cnt].find_all("td")

        due_ori = "20" + tds[3].text.lstrip().rstrip()[11:].replace(".","-",2)
        due_flag = check_date(due_ori)
        title = trs[tr_cnt].find("a")
        name = title.text.lstrip().rstrip()
        identifier = intcNo_p.search(title.get("href")).group()
        url = BASE_URL % identifier
        while (1):
            try:
                #print('kocca', name, url, due_ori, due_flag, identifier, flag)
                write_data('kocca', name, url, due_ori, due_flag, identifier, flag)
                break
            except:
                print("Write error")
def kocca():
    # page를 변경할 변수를 선언한다.
    page = 1
    # while을 종료할수있는 플래그를 만든다.
    end_flag = False
    all_trs = []
    data = read_data("kocca")

    INPUT_URL = "http://www.kocca.kr/cop/pims/list.do?menuNo=200828&recptSt=%d"

    req = requests.get(INPUT_URL % page, verify=False)  # verify를 false를 주지않으면 받아오질 못함; ssl오류남;
    # 페이지의 element 모두가져오기
    html_parse = req.text
    soup = BeautifulSoup(html_parse, 'html.parser')
    try :
        last_page_cnt = int(p.search(pageIndex_p.search(soup.find("div", {"class":"paging"}).find("a", {"class":"last"}).get("href")).group()).group())
    except :
        last_page_cnt = int(soup.find("div", {"class":"paging"}).find_all("span")[-1].text)

    if data:
        print("is data")
        data_cnt = len(data)
        data_index = data_cnt - 1
        new_post = 0

        for n in range(data_cnt):
            if (len(data[data_index - n]['due']) == 10):
                if (now_date > data[data_index - n]['due']):  # due
                    continue
            last_identifier = data[data_index - n]['identify']  # identifier
            print(last_identifier)
            break

        for page in range(last_page_cnt):
            page = page + 1

            if end_flag:
                break
            input_url = INPUT_URL % page
            req = requests.get(input_url, verify=False)  # verify를 False를 주지않으면 받아오질 못함; SSL오류남;
            # 페이지의 element 모두가져오기
            html_parse = req.text
            soup = BeautifulSoup(html_parse, 'html.parser')
            # 사업명이 들어있는 필드에 접근해서 모든 사업명을 total_title이    라는 변수에 넣는답
            trs = soup.find("div", {"class":"board_list_typea"}).find("tbody").find_all("tr")
            all_trs += trs
            for tr_cnt in range(len(trs)):
                title = trs[tr_cnt].find("a")
                identifier = intcNo_p.search(title.get("href")).group()
                print(identifier)
                if (identifier == last_identifier):
                    end_flag = True
                    break
                new_post += 1
        if (new_post):
            all_trs = all_trs[:new_post]
            all_trs.reverse()
            kocca_send_data(all_trs, ADDITIONAL_CRAWLING)
    else:
        print("no data")
        for page in range(last_page_cnt):
            page = page + 1
            if end_flag:
                break

            input_url = INPUT_URL % page
            req = requests.get(input_url, verify=False)  # verify를 false를 주지않으면 받아오질 못함; ssl오류남;
            # 페이지의 element 모두가져오기
            html_parse = req.text
            soup = BeautifulSoup(html_parse, 'html.parser')
            # 사업명이 들어있는 필드에 접근해서 모든 사업명을 total_title이    라는 변수에 넣는답
            trs = soup.find("div", {"class":"board_list_typea"}).find("tbody").find_all("tr")
            all_trs += trs
        all_trs.reverse()
        kocca_send_data(all_trs, INITIAL_CRAWLING)
    return


def kipa_send_data(trs, flag):
    BASE_URL ="http://www.kipa.org/kipa/notice/kw_0403_01.jsp?%s"
    for tr_cnt in range(len(trs)):
        tds = trs[tr_cnt].find_all("td")

        try :
            due_ori = tds[3].text.lstrip().rstrip()
        except :
            due_ori = ""

        if due_ori=="":
           continue

        due_flag = check_date(due_ori)
        title = trs[tr_cnt].find("a")
        name = title.text.lstrip().rstrip()
        identifier = article_no_p.search(title.get("href")).group()
        url = BASE_URL % identifier
        while (1):
            try:
                #print('kipa', name, url, due_ori, due_flag, identifier, flag)
                write_data('kipa', name, url, due_ori, due_flag, identifier, flag)
                break
            except:
                print("Write error")
def kipa():
    # 글의 기본 url이다.
    BASE_URL ="http://www.kipa.org/kipa/notice/kw_0403_01.jsp?%s"

    # page를 변경할 변수를 선언한다.
    page = 1
    # while을 종료할수있는 플래그를 만든다.
    end_flag = False
    all_trs = []
    data = read_data("kipa")

    INPUT_URL = "http://www.kipa.org/kipa/notice/kw_0403_01.jsp?mode=list&board_no=28&pager.offset=%d"

    req = requests.get(INPUT_URL % page, verify=False)  # verify를 false를 주지않으면 받아오질 못함; ssl오류남;
    # 페이지의 element 모두가져오기
    html_parse = req.text
    soup = BeautifulSoup(html_parse, 'html.parser')
    try :
        last_page_cnt = int(int(p.search(pager_offset_p.search(soup.find("div", {"class":"paginate"}).find_all("a")[-1].get("href")).group()).group())/10+1)
    except :
        last_page_cnt = int(int(p.search(pager_offset_p.search(soup.find("div", {"class":"paginate"}).find_all("a")[-1].get("href")).group()).group())/10+1)

    if data:
        print("is data")
        data_cnt = len(data)
        data_index = data_cnt - 1
        new_post = 0

        for n in range(data_cnt):
            if (len(data[data_index - n]['due']) == 10):
                if (now_date > data[data_index - n]['due']):  # due
                    continue
            last_identifier = data[data_index - n]['identify']  # identifier
            print(last_identifier)
            break

        for page in range(last_page_cnt):

            if end_flag:
                break
            input_url = INPUT_URL % (page*10)
            req = requests.get(input_url, verify=False)  # verify를 False를 주지않으면 받아오질 못함; SSL오류남;
            # 페이지의 element 모두가져오기
            html_parse = req.text
            soup = BeautifulSoup(html_parse, 'html.parser')
            # 사업명이 들어있는 필드에 접근해서 모든 사업명을 total_title이    라는 변수에 넣는답
            trs = soup.find("table", {"class":"list_table"}).find("tbody").find_all("tr")
            all_trs += trs
            for tr_cnt in range(len(trs)):
                title = trs[tr_cnt].find("a")
                identifier = article_no_p.search(title.get("href")).group()
                if (identifier == last_identifier):
                    end_flag = True
                    break
                new_post += 1
        if (new_post):
            all_trs = all_trs[:new_post]
            all_trs.reverse()
            kipa_send_data(all_trs, ADDITIONAL_CRAWLING)
    else:
        print("no data")
        for page in range(last_page_cnt):
            page = page + 1
            if end_flag :
                break

            input_url = INPUT_URL % (page*10)
            print(input_url)
            req = requests.get(input_url, verify=False)  # verify를 false를 주지않으면 받아오질 못함; ssl오류남;
            # 페이지의 element 모두가져오기
            html_parse = req.text
            soup = BeautifulSoup(html_parse, 'html.parser')
            # 사업명이 들어있는 필드에 접근해서 모든 사업명을 total_title이    라는 변수에 넣는답
            trs = soup.find("table", {"class":"list_table"}).find("tbody").find_all("tr")
            all_trs += trs
        all_trs.reverse()
        kipa_send_data(all_trs, INITIAL_CRAWLING)
    return

def kdb_send_data(trs, flag):
    BASE_URL ="http://www.kdb.or.kr/board/notice_01_view.html?%s"
    for tr_cnt in range(len(trs)):
        tds = trs[tr_cnt].find_all("td")

        due_ori = "공고일\r\n(" + tds[4].text.lstrip().rstrip().replace('/','-',2) + ")"

        due_flag = check_date(due_ori)
        title = trs[tr_cnt].find("a")
        name = title.text.lstrip().rstrip()

        if '공고' not in name :
            continue

        identifier = dbnum_p.search(title.get("href")).group()
        url = BASE_URL % identifier
        while (1):
            try:
                print('kdb', name, url, due_ori, due_flag, identifier, flag)
                write_data('kdb', name, url, due_ori, due_flag, identifier, flag)
                break
            except:
                print("Write error")
def kdb():
    # page를 변경할 변수를 선언한다.
    page = 1
    # while을 종료할수있는 플래그를 만든다.
    end_flag = False
    all_trs = []
    data = read_data("kdb")

    INPUT_URL = "http://www.kdb.or.kr/board/notice_01.html?page=%d"

    req = requests.get(INPUT_URL % page, verify=False)  # verify를 false를 주지않으면 받아오질 못함; ssl오류남;
    # 페이지의 element 모두가져오기
    html_parse = req.text
    soup = BeautifulSoup(html_parse, 'html.parser')
    try :
        last_page_cnt = int(p.search(page_p.search(soup.find("div", {"class":"wrap_pager"}).find_all("a")[-1].get("href")).group()).group())
    except :
        last_page_cnt = int(p.search(page_p.search(soup.find("div", {"class":"wrap_pager"}).find_all("a")[-1].get("href")).group()).group())

    if data:
        print("is data")
        data_cnt = len(data)
        data_index = data_cnt - 1
        new_post = 0

        for n in range(data_cnt):
            if (len(data[data_index - n]['due']) == 10):
                if (now_date > data[data_index - n]['due']):  # due
                    continue
            last_identifier = data[data_index - n]['identify']  # identifier
            print(last_identifier)
            break

        for page in range(last_page_cnt):

            if end_flag:
                break
            input_url = INPUT_URL % page
            req = requests.get(input_url, verify=False)  # verify를 False를 주지않으면 받아오질 못함; SSL오류남;
            req.encoding='euc-kr'
            # 페이지의 element 모두가져오기
            html_parse = req.text
            soup = BeautifulSoup(html_parse, 'html.parser')
            # 사업명이 들어있는 필드에 접근해서 모든 사업명을 total_title이    라는 변수에 넣는답
            trs = soup.find("table", {"class":"bbs_lst"}).find("tbody").find_all("tr")
            all_trs += trs
            for tr_cnt in range(len(trs)):
                title = trs[tr_cnt].find("a")
                identifier = dbnum_p.search(title.get("href")).group()
                if (identifier == last_identifier):
                    end_flag = True
                    break
                new_post += 1
        if (new_post):
            all_trs = all_trs[:new_post]
            all_trs.reverse()
            kdb_send_data(all_trs, ADDITIONAL_CRAWLING)
    else:
        print("no data")
        for page in range(last_page_cnt):
            page = page + 1
            if end_flag :
                break

            input_url = INPUT_URL % page
            print(input_url)
            req = requests.get(input_url, verify=False)  # verify를 false를 주지않으면 받아오질 못함; ssl오류남;
            #홈페이지의 인코딩이 다르면 이렇게 맞춰주면 데이터가 깨지지 않는다!
            req.encoding='euc-kr'
            # 페이지의 element 모두가져오기
            html_parse = req.text
            soup = BeautifulSoup(html_parse, 'html.parser')
            # 사업명이 들어있는 필드에 접근해서 모든 사업명을 total_title이    라는 변수에 넣는답
            trs = soup.find("table", {"class":"bbs_lst"}).find("tbody").find_all("tr")
            all_trs += trs
        all_trs.reverse()
        kdb_send_data(all_trs, INITIAL_CRAWLING)
    return

def gbsa_send_data(trs, flag):
    BASE_URL ="http://pms.gbsa.or.kr/ext/info/info_02_01.jsp?cmd=detail&ANNC_NO=%s"
    for tr_cnt in range(len(trs)):
        tds = trs[tr_cnt].find_all("td")

        due_ori = tds[2].text.lstrip().rstrip()[11:]
        due_flag = check_date(due_ori)
        title = trs[tr_cnt].find("a")
        name = title.text.lstrip().rstrip()

        identifier = annc_no_p.search(title.get("href")).group()
        url = BASE_URL % identifier

        while (1):
            try:
                #print('gbsa', name, url, due_ori, due_flag, identifier, flag)
                write_data('gbsa', name, url, due_ori, due_flag, identifier, flag)
                break
            except:
                print("Write error")
def gbsa():
    # page를 변경할 변수를 선언한다.
    page = 1
    # while을 종료할수있는 플래그를 만든다.
    end_flag = False
    all_trs = []
    data = read_data("gbsa")

    INPUT_URL = "http://pms.gbsa.or.kr/ext/info/info_02.jsp?menuId=2&leftId=2&pageNo=%d"

    req = requests.get(INPUT_URL % page, verify=False)  # verify를 false를 주지않으면 받아오질 못함; ssl오류남;
    # 페이지의 element 모두가져오기
    html_parse = req.text
    soup = BeautifulSoup(html_parse, 'html.parser')
    last_page_cnt = int(p.search(value_p.search(soup.find("div", {"id":"pageno"}).find("div",{"class":"paging"}).find_all("a")[-1].get("href")).group()).group())

    if data:
        print("is data")
        data_cnt = len(data)
        data_index = data_cnt - 1
        new_post = 0

        for n in range(data_cnt):
            if (len(data[data_index - n]['due']) == 10):
                if (now_date > data[data_index - n]['due']):  # due
                    continue
            last_identifier = data[data_index - n]['identify']  # identifier
            print(last_identifier)
            break

        for page in range(last_page_cnt):

            if end_flag:
                break
            input_url = INPUT_URL % page
            req = requests.get(input_url, verify=False)  # verify를 False를 주지않으면 받아오질 못함; SSL오류남;
            # 페이지의 element 모두가져오기
            html_parse = req.text
            soup = BeautifulSoup(html_parse, 'html.parser')
            # 사업명이 들어있는 필드에 접근해서 모든 사업명을 total_title이    라는 변수에 넣는답
            trs = soup.find("table", {"class":"table_01"}).find("tbody").find_all("tr")
            all_trs += trs
            for tr_cnt in range(len(trs)):
                title = trs[tr_cnt].find("a")
                identifier = annc_no_p.search(title.get("href")).group()
                if (identifier == last_identifier):
                    end_flag = True
                    break
                new_post += 1
        if (new_post):
            all_trs = all_trs[:new_post]
            all_trs.reverse()
            gbsa_send_data(all_trs, ADDITIONAL_CRAWLING)
    else:
        print("no data")
        for page in range(last_page_cnt):
            page = page + 1
            if end_flag :
                break

            input_url = INPUT_URL % page
            print(input_url)
            req = requests.get(input_url, verify=False)  # verify를 false를 주지않으면 받아오질 못함; ssl오류남;
            #홈페이지의 인코딩이 다르면 이렇게 맞춰주면 데이터가 깨지지 않는다!
            # 페이지의 element 모두가져오기
            html_parse = req.text
            soup = BeautifulSoup(html_parse, 'html.parser')
            # 사업명이 들어있는 필드에 접근해서 모든 사업명을 total_title이    라는 변수에 넣는답
            trs = soup.find("table", {"class":"table_01"}).find("tbody").find_all("tr")
            all_trs += trs
        all_trs.reverse()
        gbsa_send_data(all_trs, INITIAL_CRAWLING)
    return

def gtp_send_data(trs, flag):
    BASE_URL ="https://pms.gtp.or.kr/web/business/webBusinessView.do?b_idx=%s"
    for tr_cnt in range(len(trs)):
        tds = trs[tr_cnt].find_all("td")

        if "~" in tds[5].text.lstrip().rstrip() :
            due_ori = tds[5].text.lstrip().rstrip()[13:]
            print(due_ori)
        else :
            due_ori = tds[5].text.lstrip().rstrip()

        due_flag = check_date(due_ori)
        title = trs[tr_cnt].find("a")
        name = title.text.lstrip().rstrip()

        identifier = p.search(title.get("onclick")).group()
        url = BASE_URL % identifier

        while (1):
            try:
                #print('gtp', name, url, due_ori, due_flag, identifier, flag)
                write_data('gtp', name, url, due_ori, due_flag, identifier, flag)
                break
            except:
                print("Write error")
def gtp():
    # page를 변경할 변수를 선언한다.
    page = 1
    # while을 종료할수있는 플래그를 만든다.
    end_flag = False
    all_trs = []
    data = read_data("gtp")

    INPUT_URL = "https://pms.gtp.or.kr/web/business/webBusinessList.do?page=%d"

    req = requests.get(INPUT_URL % page, verify=False)  # verify를 false를 주지않으면 받아오질 못함; ssl오류남;
    # 페이지의 element 모두가져오기
    html_parse = req.text
    soup = BeautifulSoup(html_parse, 'html.parser')
    last_page_cnt = int(p.search(soup.find("div", {"class":"paging"}).find_all("a")[-1].get("onclick")).group())
    if data:
        print("is data")
        data_cnt = len(data)
        data_index = data_cnt - 1
        new_post = 0

        for n in range(data_cnt):
            if (len(data[data_index - n]['due']) == 10):
                if (now_date > data[data_index - n]['due']):  # due
                    continue
            last_identifier = data[data_index - n]['identify']  # identifier
            print(last_identifier)
            break

        for page in range(last_page_cnt):
            page = page + 1
            if end_flag:
                break
            input_url = INPUT_URL % page
            print(input_url)
            req = requests.get(input_url, verify=False)  # verify를 False를 주지않으면 받아오질 못함; SSL오류남;
            # 페이지의 element 모두가져오기
            html_parse = req.text
            soup = BeautifulSoup(html_parse, 'html.parser')
            # 사업명이 들어있는 필드에 접근해서 모든 사업명을 total_title이    라는 변수에 넣는답
            trs = soup.find("table", {"class":"t01"}).find("tbody").find_all("tr")
            all_trs += trs
            for tr_cnt in range(len(trs)):
                title = trs[tr_cnt].find("a")
                identifier = p.search(title.get("onclick")).group()
                if (identifier == last_identifier):
                    end_flag = True
                    break
                new_post += 1
        if (new_post):
            all_trs = all_trs[:new_post]
            all_trs.reverse()
            gtp_send_data(all_trs, ADDITIONAL_CRAWLING)
    else:
        print("no data")
        for page in range(last_page_cnt):
            page = page + 1
            if end_flag :
                break

            input_url = INPUT_URL % page
            print(input_url)
            req = requests.get(input_url, verify=False)  # verify를 false를 주지않으면 받아오질 못함; ssl오류남;
            #홈페이지의 인코딩이 다르면 이렇게 맞춰주면 데이터가 깨지지 않는다!
            # 페이지의 element 모두가져오기
            html_parse = req.text
            soup = BeautifulSoup(html_parse, 'html.parser')
            # 사업명이 들어있는 필드에 접근해서 모든 사업명을 total_title이    라는 변수에 넣는답
            trs = soup.find("table", {"class":"t01"}).find("tbody").find_all("tr")
            all_trs += trs
        all_trs.reverse()
        gtp_send_data(all_trs, INITIAL_CRAWLING)
    return


#send_to_marketing("크롤링 시작합니다잉?")

#bizinfo()
#kstratup()
#snventure()
#smtech()
ripc()
#egbiz()
#nipa()
#kocca()
#kipa()
#kdb()
#gbsa()
#gtp()
#update_due_flag()
#invis_past_biz()
#send_to_marketing("크롤링 끝났슈 피곤하니까 밥이라도 사주쇼")

#
