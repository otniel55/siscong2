# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-30 18:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('secretario', '0008_auto_20160530_1222'),
    ]

    operations = [
        migrations.AddField(
            model_name='privilegiopub',
            name='status',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
