# Generated by Django 4.0.3 on 2022-04-02 18:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('newsapi', '0004_city_code_country_code_alter_state_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newstimeseries',
            name='City',
        ),
        migrations.RemoveField(
            model_name='newstimeseries',
            name='Country',
        ),
        migrations.RemoveField(
            model_name='newstimeseries',
            name='Mentioned',
        ),
        migrations.RemoveField(
            model_name='newstimeseries',
            name='State',
        ),
    ]
