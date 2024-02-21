from django import forms

from searches.models import Artist, Song, RecordLabel, Review, Album
from django.core.exceptions import ValidationError


class ArtistForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ("name", "website", "genres")


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "user", "content")
        help_texts = {
            "content": "The Review text for the song",
            "rating": "",
        }


class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ("name", "acousticness", "danceability", "duration_ms", "energy", "instrumentalness",
                  "liveness","loudness", "speechiness", "year", "release_date", "tempo", "album",
                  "artist",)
        labels = {
            "productioncompany": ("Production company"),
        }
        help_texts = {
            "name": "The name of the song.",
            "duration_ms": "The duration of the song in ms",
            "year": "The year the song was released",
            "release_date": "The date the song was released",

        }
        widgets = {"name": forms.TextInput(attrs={"placeholder": "The song name"}),
                   "acousticness": forms.TextInput(attrs={"placeholder": "#.###"}),
                   "danceability": forms.TextInput(attrs={"placeholder": "#.###"}),
                   "duration_ms": forms.TextInput(attrs={"placeholder": "#####"}),
                   "energy": forms.TextInput(attrs={"placeholder": "#.#####"}),
                   "instrumentalness": forms.TextInput(attrs={"placeholder": "#.####"}),
                   "liveness": forms.TextInput(attrs={"placeholder": "#.####"}),
                   "loudness": forms.TextInput(attrs={"placeholder": "+-##.###"}),
                   "speechiness": forms.TextInput(attrs={"placeholder": "#.####"}),
                   "year": forms.TextInput(attrs={"placeholder": "YYYY"}),
                   "release_date": forms.TextInput(attrs={"placeholder": "YYYY-MM-DD"}),
                   "tempo": forms.TextInput(attrs={"placeholder": "##.###"}),
                   }

class AlbumMediaForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ["cover",]

class SearchForm(forms.Form):

    # title, genre, production company, collection models are used here
    search = forms.CharField(min_length=0,required=False)
    search_in = forms.ChoiceField(required=False,
                                  choices=(
                                      ("name", "Song name"),
                                      ("year", "Year"),
                                      ("artist", "Artist name"),
                                      ("album", "Album name"),
                                      ('genre', 'Genre'),
                                      ('record_label', 'Record Label'),
                                      ('record_label_location', 'Record label location'),
                                  )
                                  )
    search_choice = forms.ChoiceField(
        choices=RecordLabel.Locations.choices,
        required=False,
    )

    # this overwrites the clean functionality
    # prevents the user from enterting in 0 data for a search.
    def clean(self):
        self.fields['search'].required = False
        cleaned_data =super().clean()
        search_in_value = cleaned_data.get('search_in')
        search_value = cleaned_data.get('search')


        if search_in_value != 'record_label_location' and search_value == "":
            raise ValidationError(
                "You cannot leave Search Blank & not have a Record Label Location selected"
            )