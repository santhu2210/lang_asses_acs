# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-01-10 07:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appserver', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='is_edit',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='document',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]
