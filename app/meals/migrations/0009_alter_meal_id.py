# Generated by Django 3.2.16 on 2022-10-23 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0008_auto_20211024_0626'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meal',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]