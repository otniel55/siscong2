# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-01 17:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('secretario', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publicador',
            name='fechaBau',
            field=models.CharField(max_length=10),
        ),
    ]
