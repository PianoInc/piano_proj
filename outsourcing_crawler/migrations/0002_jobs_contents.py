# Generated by Django 2.0.4 on 2018-05-24 05:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outsourcing_crawler', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobs',
            name='contents',
            field=models.CharField(default=0, max_length=16),
            preserve_default=False,
        ),
    ]
