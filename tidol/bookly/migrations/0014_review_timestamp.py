# Generated by Django 5.0.3 on 2024-05-05 17:46

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookly', '0013_alter_history_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]