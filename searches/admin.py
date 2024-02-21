from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

# Register your models here.
from searches.models import RecordLabel, Album, Genre, Artist, \
    Song, ArtistGenre, AlbumRecordLabel, Review



# changing some headers + titles
class UrMixAdminSite(AdminSite):
    title_header = 'UrMix'
    site_header = 'UrMix'
    index_title = 'UrMix Admin site'

# creating an object of class
admin_site = UrMixAdminSite(name="UrMix")

class AlbumAdmin(admin.ModelAdmin):
    search_fields = ('name',)

class ArtistAdmin(admin.ModelAdmin):
    search_fields = ('name',)

class GenreAdmin(admin.ModelAdmin):
    search_fields = ('genre',)

class SongAdmin(admin.ModelAdmin):
    date_hierarchy = 'release_date'
    list_filter = ('artist', 'album')
    list_display = ('name', 'artist', 'album',)

class ReviewAdmin(admin.ModelAdmin):
    date_hierarchy = 'date_edited'
    list_filter = ('user', 'rating', 'song',)

class RecordLabelAdmin(admin.ModelAdmin):
    list_filter = ('location', 'name')
    list_display = ('name', 'location', 'website')

# adding the models to admin_site
admin_site.register(RecordLabel, RecordLabelAdmin)
admin_site.register(Album, AlbumAdmin)
admin_site.register(Genre, GenreAdmin)
admin_site.register(Artist, ArtistAdmin)
admin_site.register(Song, SongAdmin)
admin_site.register(ArtistGenre)
admin_site.register(AlbumRecordLabel)
admin_site.register(Review, ReviewAdmin)
# administration users and groups are added
#admin_site.register(User)
#admin_site.register(Group)