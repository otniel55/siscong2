# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-14 14:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('secretario', '0006_informe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publicador',
            name='fechaBau',
            field=models.CharField(max_length=10, verbose_name='Fecha de Bautismo'),
        ),
        migrations.AlterField(
            model_name='publicador',
            name='fechaNa',
            field=models.DateField(verbose_name='Fecha de Nacimiento'),
        ),
    ]
