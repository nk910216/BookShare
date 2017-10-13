# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-13 12:53
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0006_book_targeted_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='targeted_by',
            field=models.ManyToManyField(blank=True, related_name='target_books', to=settings.AUTH_USER_MODEL),
        ),
    ]
