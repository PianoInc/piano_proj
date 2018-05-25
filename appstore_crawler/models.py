from django.db import models

class AppstoreCrawler(models.Model):
    search_word = models.CharField(max_length=1024)
    search_url = models.CharField(max_length=1024)
    review_url = models.CharField(max_length=1024)

class AppInfo(models.Model):
    app_id = models.CharField(max_length=16, primary_key=True)
    title = models.CharField(max_length=256)
    size = models.CharField(max_length=16)
    lang = models.CharField(max_length=128)
    app_rating = models.CharField(max_length=2)
    icon_url = models.CharField(max_length=512)

class AppImage(models.Model):
    app_id = models.CharField(max_length=16, primary_key=True)
    img_url_0 = models.CharField(max_length=512)
    img_url_1 = models.CharField(max_length=512)
    img_url_2 = models.CharField(max_length=512)
    img_url_3 = models.CharField(max_length=512)
    img_url_4 = models.CharField(max_length=512)
    img_url_5 = models.CharField(max_length=512)
    img_url_6 = models.CharField(max_length=512)
    img_url_7 = models.CharField(max_length=512)
    img_url_8 = models.CharField(max_length=512)
    img_url_9 = models.CharField(max_length=512)

class AppReview(models.Model):
    app_id = models.CharField(max_length=16)
    author = models.CharField(max_length=16)
    rating = models.CharField(max_length=2)
    title = models.CharField(max_length=128)
    review = models.CharField(max_length=512)
