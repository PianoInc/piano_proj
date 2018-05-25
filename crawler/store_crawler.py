from urllib.request import urlopen
from urllib import parse
import json
from collections import OrderedDict
from pprint import pprint
from datetime import datetime
import requests
import sys
import os
import re
import win32com.client

sys.path.insert(0, 'e:\piano_proj\\venv\Scripts\piano_proj')
# Python이 실행될 때 DJANGO_SETTINGS_MODULE이라는 환경 변수에 현재 프로젝트의 settings.py파일 경로를 등록합니다.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "piano_proj.settings")
# 이제 장고를 가져와 장고 프로젝트를 사용할 수 있도록 환경을 만듭니다.
import django
from django.utils import timezone
django.setup()

from appstore_crawler.models import *
from rocket_bot.rocket_bot import send_to_marketing

crawler_info = AppstoreCrawler.objects.filter(id=1).values()

search_words = crawler_info[0]['search_word'].split(',')
search_url = crawler_info[0]['search_url']
review_url = crawler_info[0]['review_url']
"""
if search_words :
    for word in search_words :
        print(word)
if flag :
    msg = "%s에서 새로운 공고가 떳어요\n %s \n 링크는 여기! \n%s \n 기한은 %s 까지니까 서두르세요!\n Good Luck!\n------------------------------------------------------------------------------------------------------\n" % (site_name, name, url, due)
    send_to_marketing(msg)
"""

def is_app_id(app_id):
    if AppInfo.objects.filter(app_id=app_id) :
        return True
    return False

def write_appinfo(id, name, size, lang, rating, icon) :
    data = AppInfo(app_id=id,title=name,size=size,lang=lang, app_rating=rating, icon_url=icon)
    data.save()
    return

def write_appimage(id, img) :
    data = AppImage(app_id=id,img_url_0=img[0],img_url_1=img[1],img_url_2=img[2],img_url_3=img[3],
                   img_url_4=img[4],img_url_5=img[5],img_url_6=img[6],img_url_7=img[7],img_url_8=img[8],img_url_9=img[9])
    data.save()
    return

def write_appreview(app_id, author, rating, title, review) :
    data = AppReview(app_id=app_id, author=author, rating=rating, title=title, review=review)
    data.save()
    return

def appstore_crawler() :
    for word in search_words :
        with urlopen(search_url % parse.quote(word)) as res:
            res_data = res.read()

            #json 파일저장
            json_path = "./data/"
            if not os.path.isdir(json_path):
                os.mkdir(json_path)
            with open('%s%s.json' % (json_path,word), 'wb') as f:
                f.write(res_data)
                f.close()

            #json 파일열기
            with open('%s%s.json' % (json_path,word), encoding="utf-8") as data_file:
                app_data = json.load(data_file, object_pairs_hook=OrderedDict)

            #데이터 분류
            for index in range(app_data["resultCount"]):

                app_id = app_data["results"][index]["trackId"]#app의 ID
                app_name = app_data["results"][index]["trackCensoredName"]#app의 이름
                if is_app_id(app_id) :
                    print("AppID [%s]is already exist!" % app_id)
                    continue
                else :
                    msg = "새로운 앱 정보가 추가되었습니다.\n앱 이름 : %s\nhttp://192.168.0.6:8000/appstore_crawler/show_list/detail/%s/\n" % (app_name,app_id)
                    send_to_marketing(msg)

                data_path = "%s%s" % (json_path,re.sub("[/|:*\"<> ]", "",app_data["results"][index]["trackCensoredName"])) + "/"
                try :
                    app_rating = [index]["averageUserRatingForCurrentVersion"]
                except :
                    app_rating = 0

                support_lang = app_data["results"][index]["languageCodesISO2A"]# 지원 언어
                app_size = app_data["results"][index]["fileSizeBytes"]#파일사이즈
                app_icon = app_data["results"][index]["artworkUrl100"]# 100X100 아이콘 이미지
                write_appinfo(app_id, app_name, app_size, support_lang, app_rating, app_icon)

                if not os.path.isdir(data_path):
                    os.mkdir(data_path)

                img_list = ["null","null","null","null","null","null","null","null","null","null","null"]
                for img_index, img in enumerate(app_data["results"][index]["screenshotUrls"]):  # 스크린샷 이미지
                    if img_index >= 0:
                        img_list[img_index] = img
                write_appimage(app_id, img_list)
                ####################################################################REVIEW COLLECT####################################################################
                no = 1
                for page_no in range (10) :
                    url = review_url % (page_no+1, app_id)

                    try :
                        with urlopen(url) as res:
                            res_data = res.read()
                            # json 파일저장
                            with open('%s%s_page%02d.json' % (data_path, word, page_no), 'wb') as f:
                                f.write(res_data)
                                f.close()
                            with open('%s%s_page%02d.json' % (data_path, word, page_no), encoding="utf-8") as data_file:
                                data = json.load(data_file, object_pairs_hook=OrderedDict)

                            try :
                                comment_data = data["feed"]["entry"]
                            except :
                                break

                            for d in data["feed"]["entry"] :
                                try :
                                    author = "("+d["author"]["name"]["label"]+")"
                                except :
                                    continue
                                rating = d["im:rating"]["label"]
                                title = d["title"]["label"]
                                review = d["content"]["label"]
                                write_appreview(app_id, author, rating, title, review)
                                no += 1
                    except :
                        print('error idx = %s(%s)' % (app_name,app_id))
                        break

                ####################################################################EXCEL CLOSE####################################################################

appstore_crawler()
