# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-08 10:03
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0007_executionsummary'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='executionsummary',
            options={'verbose_name_plural': 'Execution Summary'},
        ),
    ]
