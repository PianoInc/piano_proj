# Generated by Django 2.0.4 on 2018-04-29 17:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appstore_crawler', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AppIcon',
        ),
        migrations.DeleteModel(
            name='AppImage',
        ),
        migrations.DeleteModel(
            name='AppInfo',
        ),
        migrations.DeleteModel(
            name='AppReview',
        ),
    ]