import csv
import re
import pandas as pd
from datetime import datetime
from django.utils import timezone

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from searches.models import RecordLabel, Album, Genre, Artist, \
    Song, ArtistGenre, AlbumRecordLabel, Review



class Command(BaseCommand):
    help = 'Load the reviews data from a CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('--csv', type=str)

    @staticmethod
    def row_to_dict(row, header):
        if len(row) < len(header):
            row += [''] * (len(header) - len(row))
        print("", dict([(header[i], row[i]) for i, head in enumerate(header) if head]))
        return dict([(header[i], row[i]) for i, head in enumerate(header) if head])

    def handle(self, *args, **options):
        m = re.compile(r'content:(\w+)')
        header = None
        models = dict()
        try:
            with open(options['csv']) as csvfile:
                model_data = csv.reader(csvfile)
                for i, row in enumerate(model_data):
                    if max([len(cell.strip()) for cell in row[1:] + ['']]) == 0 and m.match(row[0]):
                        model_name = m.match(row[0]).groups()[0]
                        models[model_name] = []
                        header = None
                        continue

                    if header is None:
                        header = row
                        continue

                    row_dict = self.row_to_dict(row, header)
                    if set(row_dict.values()) == {''}:
                        continue
                    models[model_name].append(row_dict)

        except FileNotFoundError:
            raise CommandError('File "{}" does not exist'.format(options['csv']))

        for data_dict in models.get('RecordLabel', []):
            p, created = RecordLabel.objects.get_or_create(
                name=data_dict['recordlabel_name'], defaults={
                    'website': data_dict['recordlabel_website'],
                    'location': data_dict['recordlabel_location']
                })

            if created:
                print('Created RecordLabel "{}"'.format(p.name))

        for data_dict in models.get('Album', []):
            b, created = Album.objects.get_or_create(
                name=data_dict['album_name'],
                defaults={
                    'asin': data_dict['album_asin'],
                })

            if created:
                print('Created Album "{}"'.format(b.name))

        for data_dict in models.get('Genre', []):
            c, created = Genre.objects.get_or_create(
                genre=data_dict['genre_genre'],
                description=data_dict['genre_description'],
            )

            if created:
                print(f'Created Genre {c.genre}')

        # may need to put a try catch in here somewhere, to catch collection?
        for data_dict in models.get('Artist', []):

            c, created = Artist.objects.get_or_create(
                name=data_dict['artist_name'],
                website=data_dict['artist_website']
            )



        for data_dict in models.get('Song', []):

            if data_dict['song_release_date'] == "":
                data_dict['song_release_date'] = None

            try:
                c, created = Song.objects.get_or_create(


                    name=data_dict['song_name'],
                    acousticness=data_dict['song_acousticness'],
                    danceability=data_dict['song_danceability'],
                    duration_ms=data_dict['song_duration_ms'],
                    energy=data_dict['song_energy'],
                    instrumentalness=data_dict['song_instrumentalness'],
                    liveness=data_dict['song_liveness'],
                    loudness=data_dict['song_loudness'],
                    speechiness=data_dict['song_speechiness'],
                    year=data_dict['song_year'],
                    release_date=data_dict['song_release_date'],
                    tempo=data_dict['song_tempo'],
                    artist=Artist.objects.get(name=data_dict['song_artist']),
                    album=Album.objects.get(name=data_dict['song_album']),


                )
            except Exception as e:
                print(e)
                print(f"Value is: {type(data_dict['song_release_date'])}")
                print(data_dict["song_release_date"] is None)
                print(data_dict["song_release_date"] == "")
                input("continue...")


            if created:
                print(f'Created Song {c.name}: {c.release_date}')

        for data_dict in models.get('ArtistGenre', []):
            c, created = ArtistGenre.objects.get_or_create(
                artist=Artist.objects.get(name=data_dict['artistgenre_artist']),
                genre=Genre.objects.get(genre=data_dict['artistgenre_genre']),
            )

            if created:
                print(f'Created ArtistGenre {c}')

        for data_dict in models.get('AlbumRecordLabel', []):

            creator, created = AlbumRecordLabel.objects.get_or_create(
                album=Album.objects.get(name=data_dict['albumrecordlabel_album']),
                record_label=RecordLabel.objects.get(name=data_dict['albumrecordlabel_recordlabel']),
            )

        for data_dict in models.get('Review', []):

            creator, created = User.objects.get_or_create(
                email=data_dict['review_user'],
                username=data_dict['review_user'],
            )
            if created:
                print('Created User "{}"'.format(creator.email))

            date_cre = data_dict['review_date_created']
            date_edi = data_dict['review_date_edited']

            date_cre = date_cre.replace("/", "-")
            date_edi = date_edi.replace("/", "-")

            #if date_edi == "":
            #    date_edi = None

            date_cre = pd.to_datetime(date_cre)
            date_edi = pd.to_datetime(date_edi)

            date_cre = timezone.make_aware(date_cre, timezone=timezone.get_current_timezone())
            date_edi = timezone.make_aware(date_edi, timezone=timezone.get_current_timezone())


            review, created = Review.objects.get_or_create(
                rating=data_dict['review_rating'],
                content=data_dict['review_content'],
                date_created=date_cre,
                date_edited=date_edi,
                user=creator,
                song=Song.objects.get(name=data_dict['review_song']),
            )

            if created:
                print(f'Created Review {review.user_id}')


    print("Import complete")