# Generated by Django 2.0.4 on 2018-04-29 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appstore_crawler', '0005_appicon_appimage_appinfo_appreview'),
    ]

    operations = [
        migrations.CreateModel(
            name='AoppstoreCrawler',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search_word', models.CharField(max_length=1024)),
                ('search_url', models.CharField(max_length=1024)),
                ('review_url', models.CharField(max_length=1024)),
            ],
        ),
        migrations.RenameField(
            model_name='appinfo',
            old_name='id',
            new_name='app_id',
        ),
        migrations.RenameField(
            model_name='appreview',
            old_name='comment',
            new_name='review',
        ),
    ]