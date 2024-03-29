# Generated by Django 3.2.18 on 2023-07-15 16:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_profile_id'),
        ('carts', '0012_alter_cart_details_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='profile',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to='users.profile'),
        ),
        migrations.AlterUniqueTogether(
            name='cart',
            unique_together={('yearweek', 'profile')},
        ),
    ]
