# Generated by Django 5.0.3 on 2024-04-25 01:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookly', '0005_alter_chapter_chapter_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='cover',
            field=models.ImageField(null=True, upload_to='covers/'),
        ),
    ]