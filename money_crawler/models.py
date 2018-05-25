from django.db import models

class Business(models.Model):
        idx = models.AutoField(primary_key=True)
        title = models.CharField(max_length=256)
        url = models.CharField(max_length=512)
        due = models.CharField(max_length=32)
        due_flag = models.CharField(max_length=16)
        identify = models.CharField(max_length=512, unique=True, null=False)
        site = models.CharField(max_length=64)
        save_date = models.DateTimeField()
        vis = models.BooleanField()
        fav = models.BooleanField()
