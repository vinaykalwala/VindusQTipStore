# Generated by Django 5.1.7 on 2025-03-29 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Orders', '0012_alter_order_total_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='total_price',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
