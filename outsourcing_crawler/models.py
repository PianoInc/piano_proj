from django.db import models

class Jobs(models.Model):
    idx = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    url = models.CharField(max_length=512)
    price = models.CharField(max_length=128)
    due = models.CharField(max_length=64)
    period = models.CharField(max_length=64)
    due_flag = models.CharField(max_length=16)
    contents = models.CharField(max_length=4096)
    identify = models.CharField(max_length=512, unique=True, null=False)
    site = models.CharField(max_length=64)
    save_date = models.DateTimeField()
    vis = models.BooleanField()
    fav = models.BooleanField()

