# Generated by Django 2.2.10 on 2020-04-12 04:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0006_auto_20200120_2101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meal',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]