# Generated by Django 2.2.24 on 2021-10-24 06:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ingredients', '__first__'),
        ('carts', '0008_cart_details_found'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart_details',
            name='ingredient',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to='ingredients.Ingredient'),
        ),
    ]
