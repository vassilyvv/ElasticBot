# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-14 16:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BotCommand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(blank=True, null=True)),
                ('method', models.PositiveSmallIntegerField(choices=[(1, 'GET'), (2, 'POST')], default=1)),
                ('name', models.CharField(max_length=255)),
                ('message', models.CharField(max_length=255)),
                ('answer_regex', models.CharField(blank=True, max_length=255, null=True)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tgbot.BotCommand')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LastCommand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tg_user_id', models.BigIntegerField(unique=True)),
                ('command', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tgbot.BotCommand')),
            ],
        ),
        migrations.CreateModel(
            name='PostParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.PositiveSmallIntegerField(choices=[(1, 'Boolean'), (2, 'Integer'), (3, 'String')])),
                ('name', models.CharField(max_length=20)),
                ('key', models.CharField(max_length=20)),
                ('value', models.TextField(blank=True, null=True)),
                ('bot_command', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_params', to='tgbot.BotCommand')),
            ],
        ),
        migrations.CreateModel(
            name='SavedPostParameter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(blank=True, null=True)),
                ('tg_user_id', models.BigIntegerField()),
                ('post_parameter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tgbot.PostParam')),
            ],
        ),
        migrations.CreateModel(
            name='SavedUrlParameter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(blank=True, null=True)),
                ('tg_user_id', models.BigIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='UrlParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=20)),
                ('value', models.CharField(blank=True, max_length=255, null=True)),
                ('name', models.CharField(max_length=20)),
                ('bot_command', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='url_params', to='tgbot.BotCommand')),
            ],
        ),
        migrations.AddField(
            model_name='savedurlparameter',
            name='url_parameter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tgbot.UrlParam'),
        ),
    ]
