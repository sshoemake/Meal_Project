# Generated by Django 2.2.24 on 2021-10-24 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('aisle', models.DecimalField(decimal_places=1, max_digits=4)),
                ('auto_add', models.BooleanField()),
            ],
            options={
                'ordering': ['aisle'],
            },
        ),
    ]
