# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-08-31 15:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geo_admin', '0010_auto_20180413_0710'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='road',
            name='postal_code',
        ),
    ]
