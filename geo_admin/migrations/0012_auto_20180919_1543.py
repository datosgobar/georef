# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-09-19 15:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geo_admin', '0011_auto_20180831_1553'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='municipality',
            name='department',
        ),
    ]
