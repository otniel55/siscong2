# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-18 15:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('secretario', '0004_auto_20160418_1033'),
    ]

    operations = [
        migrations.AddField(
            model_name='informe',
            name='observacion',
            field=models.CharField(default='no hay', max_length=250),
            preserve_default=False,
        ),
    ]