from django.db import models
from django.contrib import auth


# Create your models here.
class RecordLabel(models.Model):

    class Locations(models.TextChoices):
        LONDON = "LDN", "London, England"
        NEW_YORK = "NY", "New York City, US"
        CALIFORNIA = "CA", "California, US"
        OAKLAND = "0-Town", "Oakland, US"
        FLORIDA = "FL", "Florida, US"
        SWEDEN = "SE", "Sweden"
        BARCELONA = "BCN", "Barcelona, Spain"
        MEXICO_CITY = "CDMX", "Mexico City, Mexico"
        MILAN = "MI", "Milan Italy"
        UNITED_KINGDOM = "UK", "United Kingdom"
        MANHATTAN = "MNY", "Manhattan, US"

    name = models.CharField(
        max_length=75,
        help_text="Name of the Record Label.",

    )
    website = models.CharField(
        max_length=200,
    )

    location = models.CharField(
        max_length=6,
        choices=Locations.choices,
        verbose_name="The location of the label",

    )

    albums = models.ManyToManyField("Album", through="AlbumRecordLabel")


    def __str__(self):
        return f"{self.name}"



class Album(models.Model):
    name = models.CharField(
        max_length=60,
        help_text="Name of the Record Label."
    )
    asin = models.CharField(
        max_length=10,
        help_text="Amazon Standard Identification Number"
    )
    cover = models.ImageField(null=True,
                              blank=True,
                              upload_to='images/')

    record_labels = models.ManyToManyField("RecordLabel", through="AlbumRecordLabel")

    def __str__(self):
        return self.name


class Genre(models.Model):
    genre = models.CharField(
        max_length=25,
    )
    description = models.TextField(
        help_text="Description of Genre."
    )

    artists = models.ManyToManyField("Artist", through="ArtistGenre",related_name="art")

    def __str__(self):
        return f"{self.genre}"


class Artist(models.Model):
    name=models.CharField(
        max_length=20,
    )
    website = models.CharField(
        max_length=200,

    )
    genres = models.ManyToManyField(Genre, through="ArtistGenre")

    def __str__(self):
        return self.name


class Song(models.Model):
    name = models.CharField(
        max_length=60,
    )
    acousticness = models.FloatField(

    )
    danceability = models.FloatField(

    )
    duration_ms = models.IntegerField(

    )
    energy = models.FloatField(

    )
    instrumentalness = models.FloatField(

    )
    liveness = models.FloatField(

    )
    loudness = models.FloatField(

    )
    speechiness = models.FloatField(

    )
    year = models.IntegerField(

    )
    release_date = models.DateField(
        blank=True,
        null=True,
    )
    tempo = models.FloatField(
    )

    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        null=True,
    )

    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name



class ArtistGenre(models.Model):
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE
    )
    # genre and artist id are foreign keys, come back to this.

    def __str__(self):
        return f"{self.artist} ({self.genre.genre})"

class AlbumRecordLabel(models.Model):
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE
    )
    record_label = models.ForeignKey(
        RecordLabel,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.album} ({self.record_label})"


class Review(models.Model):
    rating = models.IntegerField(
        help_text="Rating of the song."
    )
    content = models.TextField(
        help_text="Review Content",
    )
    date_created = models.DateTimeField(
        help_text="Date that the review was created",
        auto_now_add=True,
    )
    date_edited = models.DateTimeField(
        help_text="Date that the review was edited",
        null=True,
        blank=True,

    )
    song = models.ForeignKey(
        Song, on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        auth.get_user_model(), on_delete=models.CASCADE,
    )
    # Two Foreign keys here.

    def __str__(self):
        return f"{self.song} -  {self.user} (Rating: {self.rating})"