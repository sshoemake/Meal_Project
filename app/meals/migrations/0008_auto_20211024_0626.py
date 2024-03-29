# Generated by Django 2.2.24 on 2021-10-24 06:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0009_auto_20211024_0626'),
        ('meals', '0007_auto_20200412_0424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meal_details',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ingredients.Ingredient'),
        ),
        migrations.DeleteModel(
            name='Ingredient',
        ),
    ]
