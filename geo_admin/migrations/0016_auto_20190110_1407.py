# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-01-10 14:07
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geo_admin', '0015_auto_20190110_1136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='road',
            name='geom',
            field=django.contrib.gis.db.models.fields.MultiLineStringField(srid=4326, verbose_name='geometría'),
        ),
    ]