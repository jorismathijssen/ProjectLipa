# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-05-09 21:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0003_gamesession'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamesession',
            name='duration',
            field=models.DurationField(blank=True, null=True),
        ),
    ]
