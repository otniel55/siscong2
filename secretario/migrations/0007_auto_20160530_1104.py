# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-30 15:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('secretario', '0006_auto_20160517_1528'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publicador',
            name='FKgrupo',
        ),
        migrations.AddField(
            model_name='privilegiopub',
            name='responsabilidad',
            field=models.CharField(default='Ninguna', max_length=200, verbose_name='Responsabilidad'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='publicador',
            name='grupo',
            field=models.ManyToManyField(to='secretario.GruposPred'),
        ),
        migrations.AlterField(
            model_name='grupospred',
            name='auxiliar',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pubauxiliar', to='secretario.Publicador'),
        ),
        migrations.AlterField(
            model_name='grupospred',
            name='encargado',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='secretario.Publicador'),
        ),
    ]
