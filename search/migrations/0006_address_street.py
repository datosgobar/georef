# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-22 17:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0005_address_search_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='street',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
