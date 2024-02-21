from django.shortcuts import render, redirect, get_object_or_404
from searches.forms import SearchForm, SongForm, ReviewForm, ArtistForm, AlbumMediaForm
from searches.models import Song, AlbumRecordLabel, Artist, ArtistGenre, Album, Review, Genre
from statistics import mean
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from PIL import Image, ImageFile
from io import BytesIO
from django.utils import timezone
import datetime as dt
import PIL
from django.contrib.auth import logout

#this has to be done because otherwise it complains about 405 errors when switching between
# virtual environments.
def logout_view(request):
    logout(request)
    return render(request, 'logged_out.html')

# return the profile specific to the user
@login_required
def profile(request):
    return render(request, 'profile.html')


# returns the list of reviews for a given Song in a list.
@login_required
def details_reviews(request, song_id):
    song = Song.objects.get(pk=song_id)

    review_list = song.review_set.all()

    context = {
        'song': song,
        'review_list': review_list,
    }

    return render(request, 'review_list.html', context)


# staff member required prevents normal user from accessing certain addresses
# it does redirect to a basic login page, but entering staff details at that point
# gives the correct final location
@staff_member_required
def artist_edit(request, pk):
    artist = Artist.objects.get(pk=pk)

    # if method is post, update the artist with new details.
    # then redirect to updated artist
    if request.method == "POST":
        form = ArtistForm(request.POST, instance=artist)
        if form.is_valid():
            updated_artist = form.save()
            messages.success(request, f'Artist "{updated_artist}" was updated.')
            return redirect("artist_edit", updated_artist.pk)

    #otherwise, bring up form of the artist being edited.
    else:
        form = ArtistForm(instance=artist)

        context = {
            "form": form,
            "instance": artist,
            "model_type": "Artist"
        }
    return render(request, "artist_edit.html", context=context)


# only authenticated users can access
@login_required
def review_edit(request, song_id, review_id=None):
    if review_id is not None:
        review = Review.objects.get(pk=review_id)
    else:
        review = None

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)

        # two separate review flows here:
        # if the review is None, we create a review object with details captured from user.
        # set the date_edited and date_created to now.
        if form.is_valid() and review is None:
            rating = form.cleaned_data["rating"]
            user = form.cleaned_data["user"]
            content = form.cleaned_data["content"]
            updated_review = Review.objects.create(rating=rating, user=user, content=content, song_id=song_id, date_edited = dt.datetime.now(), date_created=dt.datetime.now())
            if review is None:
                messages.success(request, f'Review "{updated_review}" was created.')
            else:
                messages.success(request, f'Review "{updated_review}" was updated.')

            return redirect("review_edit", song_id, updated_review.pk)

        # otherwise, the review is being updated.
        elif form.is_valid() and review:
            rating = form.cleaned_data["rating"]
            user = form.cleaned_data["user"]
            content = form.cleaned_data["content"]

            review.rating = rating
            review.user = user
            review.content = content
            review.date_edited = dt.datetime.now()

            # the review needs to be saved for the review object to actually be saved.
            review.save()

            if review is None:
                messages.success(request, f'Review "{review}" was created.')
            else:
                messages.success(request, f'Review "{review}" was updated.')

            return redirect("review_edit", song_id, review.pk)

    else:
        form = ReviewForm(instance=review)

        context = {
            "form": form,
            "instance": review,
            "model_type": "Review"
        }
    return render(request, "review_edit.html", context=context)



@login_required
def song_edit(request, id=None):
    song_exists = True


    if id is not None:
        song = Song.objects.get(pk=id)
    else:
        print("Song was none.")
        song = None
        song_exists = False

    # we either create or edit a song here.
    if request.method == "POST":
        print("Request method!")
        form = SongForm(request.POST, instance=song)

        if form.is_valid():
            updated_song = form.save()
            print(updated_song)
            if song is None:
                messages.success(request, f'Song "{updated_song}" was created.')
            else:
                messages.success(request, f'Song "{updated_song}" was updated.')

            return redirect("song_edit", updated_song.pk)
        else:
            messages.error(request, f'Song "{updated_song}" was invalid form.')
    else:
        form = SongForm(instance=song)
        context = {
            "form": form,
            "instance": song,
            "model_type": "Song"
        }

    # if the user is authenticated and the song exists, add it to the viewed songs list.
    if request.user.is_authenticated and song_exists:

        max_viewed_songs_length = 5
        viewed_songs = request.session.get('viewed_songs', [])
        viewed_song = [song.id, song.name]

        if viewed_song in viewed_songs:
            viewed_songs.pop(viewed_songs.index(viewed_song))

        viewed_songs.insert(0, viewed_song)
        viewed_songs = viewed_songs[:max_viewed_songs_length]
        request.session['viewed_songs'] = viewed_songs

    return render(request, "song_edit.html", context=context)


# add an image as a cover to the album object.
@staff_member_required
def album_media(request, album_pk):
    album = get_object_or_404(Album, pk=album_pk)
    if request.method == "POST":
        form = AlbumMediaForm(request.POST, request.FILES, instance=album)

        if form.is_valid():
            album = form.save(False)
            cover = form.cleaned_data.get("cover")

            if cover:
                image = Image.open(cover)
                image.thumbnail((300, 300))
                image_data = BytesIO()
                image.save(fp=image_data, format=cover.image.format)
                image_file = image_data
                album.cover.save(cover.name, image_file)

            album.save()
            messages.success(request, "Album \"{}\" was successfully updated.".format(album))
            context = {"album.pk", messages}
            return redirect("album_media", album.pk)

    else:
        form = AlbumMediaForm(instance=album)
        context = {
            "instance": album,
            "form": form,
            "model_type": "Album",
            "is_file_upload": True
        }
        return render(request, "instance-form.html", context=context)

def average_rating(reviews_ratings):
    return mean(reviews_ratings)


# this function is functionally a mess.
def song_search(request):

    song_list = list()
    search_in = ""
    search_choice = ""
    search = ""


    if request.method == "POST":
        search_text = request.POST.get("search", "")
        form = SearchForm(request.POST)
    else:

        location_text = request.GET.get("search_in", "")

        search_text = request.GET.get("search", "")
        form = SearchForm(request.GET)

        if location_text == "record_label_location":
            search_text = request.GET.get("search_choice", "")


    songs = set()
    if (form.is_valid() and form.cleaned_data["search"]) or (form.is_valid() and form.cleaned_data["search_choice"]):
        search = form.cleaned_data["search"]
        search_in = form.cleaned_data.get("search_in") or "name"
        search_choice = form.cleaned_data.get("search_choice")

        if search_in == "name":
            songs = Song.objects.filter(name__icontains=search)

        elif search_in == "year":
            songs = Song.objects.filter(year__icontains=search)

        elif search_in == "artist":
            songs = Song.objects.filter(artist__name__icontains=search)

        elif search_in == "genre":
            artist_id_list = []
            genre_query_list = ArtistGenre.objects.filter(genre__genre__icontains=search).values()
            for q in genre_query_list:
                #print(q['artist_id'])
                artist_id_list.append(q['artist_id'])

            songs = Song.objects.filter(artist__id__in=artist_id_list)

        elif search_in == "record_label":
            album_id_list = []
            record_label_query_list = AlbumRecordLabel.objects.filter(record_label__name__icontains=search).values()
            for q in record_label_query_list:
                album_id_list.append(q['album_id'])

            songs = Song.objects.filter(album__id__in=album_id_list)

        elif search_in == "record_label_location":
            album_id_list = []
            record_label_query_list = AlbumRecordLabel.objects.filter(
                record_label__location__icontains=search_choice
            ).values()
            for q in record_label_query_list:
                album_id_list.append(q['album_id'])

            songs = Song.objects.filter(album__id__in=album_id_list)

        elif search_in == "album":
            #value = Album.objects.filter(name__icontains=search)
            songs = Song.objects.filter(album__name__icontains = search)

        # this is the functionality used when search is called from top right hand corner
        else:
            songs = Song.objects.filter(name__icontains=search)

        for song in songs:
            reviews = song.review_set.all()
            album_id = song.album.id
            artist_id = song.artist.id
            record_label_names = []
            record_label_locations = []
            genre_list = []

            record_label_query_list = AlbumRecordLabel.objects.filter(album_id=album_id)
            genre_query_list = ArtistGenre.objects.filter(artist_id=artist_id)


            for v in record_label_query_list:
                record_label_names.append(v.record_label.name)
                record_label_locations.append(v.record_label.location)

            for g in genre_query_list:
                genre_list.append(g.genre.genre)

            if reviews:
                review_ratings = list()
                for review in reviews:
                    review_ratings.append(int(review.rating))
                    song_rating = str(round(average_rating(review_ratings), 2))
                    number_of_reviews = str(len(reviews))
            else:
                song_rating = None
                number_of_reviews = "0"

            song_list.append(
                {
                    'song':song,
                    'song_rating': song_rating,
                    'number_of_reviews': number_of_reviews,
                    'record_label_names': record_label_names,
                    'record_label_locations': record_label_locations,
                    'genre_list': genre_list,
                }
            )

    if request.user.is_authenticated:

        t_search = ""
        max_searches_length = 10
        viewed_searches = request.session.get('viewed_searches', [])

        if search_in == "record_label_location":
            viewed_search = [search_choice, 'location']
        else:
            t_search = search_in

            if t_search == "name":
                t_search = "song"
            elif t_search == "record_label":
                t_search = "label"

            viewed_search = [search, t_search]

        viewed_searches.insert(0, viewed_search)

        viewed_searches = viewed_searches[:max_searches_length]

        request.session['viewed_searches'] = viewed_searches

    return render(request, "search-results.html", context={
            'form': form,
            'song_list': song_list,
            "search_text": search_text,
        })
