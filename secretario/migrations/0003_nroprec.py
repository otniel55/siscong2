# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-11 12:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('secretario', '0002_auto_20160330_1754'),
    ]

    operations = [
        migrations.CreateModel(
            name='nroPrec',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nroPrec', models.IntegerField()),
                ('FKpub', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='secretario.Publicador')),
            ],
        ),
    ]