# Generated by Django 5.0.3 on 2024-04-11 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookly', '0004_alter_chapter_chapter_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chapter',
            name='chapter_number',
            field=models.DecimalField(decimal_places=2, max_digits=16, unique=True),
        ),
    ]
