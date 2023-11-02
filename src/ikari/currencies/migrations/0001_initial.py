# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-02-15 06:54
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, null=True)),
                ('code', models.CharField(max_length=20, null=True)),
                ('symbol', models.CharField(max_length=10, null=True)),
                ('is_decimal', models.BooleanField(default=True, max_length=2)),
                ('format', models.CharField(max_length=20, null=True)),
                ('create_date', models.DateField(default=datetime.date.today)),
                ('update_date', models.DateField(default=datetime.date.today)),
                ('update_by', models.CharField(max_length=50, null=True)),
                ('is_hidden', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='ExchangeRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.DecimalField(decimal_places=6, max_digits=20, null=True)),
                ('exchange_date', models.DateField(default=datetime.date.today)),
                ('description', models.CharField(blank=True, max_length=4000, null=True)),
                ('create_date', models.DateField(default=datetime.date.today)),
                ('update_date', models.DateField(default=datetime.date.today)),
                ('update_by', models.CharField(max_length=50, null=True)),
                ('is_hidden', models.BooleanField()),
                ('flag', models.CharField(blank=True, max_length=15, null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.Company')),
                ('from_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_currency', to='currencies.Currency')),
                ('to_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_currency', to='currencies.Currency')),
            ],
        ),
    ]