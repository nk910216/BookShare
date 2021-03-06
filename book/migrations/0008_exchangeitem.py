# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-17 06:55
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('book', '0007_auto_20171013_1253'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExchangeItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('fromItem', models.ManyToManyField(related_name='exchange_source', to='book.BookItem')),
                ('fromUser', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='exchange_source', to=settings.AUTH_USER_MODEL)),
                ('toItem', models.ManyToManyField(related_name='exchange_target', to='book.BookItem')),
                ('toUser', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='exchange_target', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
