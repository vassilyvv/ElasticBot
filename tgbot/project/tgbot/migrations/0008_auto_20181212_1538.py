# Generated by Django 2.1.4 on 2018-12-12 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0007_auto_20181212_1524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='botcommand',
            name='url',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
