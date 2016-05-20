# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-17 19:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('secretario', '0005_informe_observacion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='horascon',
            name='FKpub',
        ),
        migrations.RemoveField(
            model_name='horascon',
            name='mes',
        ),
        migrations.RemoveField(
            model_name='horascon',
            name='year',
        ),
        migrations.AddField(
            model_name='horascon',
            name='FKinf',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='secretario.Informe'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='publicador',
            name='email',
            field=models.CharField(max_length=200),
        ),
    ]