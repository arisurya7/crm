# Generated by Django 3.2.8 on 2022-02-20 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clustering', '0010_order_id_customer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weightrfm',
            name='id',
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
    ]
