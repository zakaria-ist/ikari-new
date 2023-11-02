# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-02-15 06:54
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('currencies', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, null=True)),
                ('code', models.CharField(max_length=20, null=True)),
                ('create_date', models.DateField(default=datetime.date.today)),
                ('update_date', models.DateField(default=datetime.date.today)),
                ('update_by', models.CharField(max_length=50, null=True)),
                ('is_hidden', models.BooleanField()),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='currencies.Currency')),
            ],
        ),
    ]