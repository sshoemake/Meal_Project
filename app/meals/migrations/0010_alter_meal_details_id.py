# Generated by Django 3.2.16 on 2022-10-23 20:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0009_alter_meal_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meal_details',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]