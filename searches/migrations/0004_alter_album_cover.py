# Generated by Django 4.2.5 on 2023-12-08 01:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('searches', '0003_rename_genre_artist_genres_album_record_labels_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='cover',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]