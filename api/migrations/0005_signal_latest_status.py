# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-05 12:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_signal_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='signal',
            name='latest_status',
            field=models.ManyToManyField(related_name='latest_status', to='api.Status'),
        ),
    ]
