# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-30 16:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('secretario', '0007_auto_20160530_1104'),
    ]

    operations = [
        migrations.AddField(
            model_name='publicador',
            name='sexo',
            field=models.CharField(default='masculino', max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='grupospred',
            name='IDgrupo',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
