# Generated by Django 3.2.8 on 2021-11-15 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='name',
            field=models.CharField(default='joe', max_length=250),
            preserve_default=False,
        ),
    ]