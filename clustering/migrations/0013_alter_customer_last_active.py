# Generated by Django 3.2.8 on 2022-03-22 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clustering', '0012_auto_20220221_0038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='last_active',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]