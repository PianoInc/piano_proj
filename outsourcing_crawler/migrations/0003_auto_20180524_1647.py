# Generated by Django 2.0.4 on 2018-05-24 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outsourcing_crawler', '0002_jobs_contents'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobs',
            name='contents',
            field=models.CharField(max_length=4096),
        ),
    ]