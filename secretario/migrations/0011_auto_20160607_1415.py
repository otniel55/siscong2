# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-06-07 18:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('secretario', '0010_privilegiopub_fechafin'),
    ]

    operations = [
        migrations.RenameField(
            model_name='informe',
            old_name='horas',
            new_name='minutos',
        ),
    ]
