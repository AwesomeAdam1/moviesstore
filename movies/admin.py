from django.contrib import admin
from .models import Movie, Review, MoviePetition, PetitionVote

class MovieAdmin(admin.ModelAdmin):
		ordering = ['name']
		search_fields = ['name']

class MoviePetitionAdmin(admin.ModelAdmin):
    list_display = ['movie_title', 'created_by', 'status', 'created_at', 'get_vote_score']
    list_filter = ['status', 'created_at']
    search_fields = ['movie_title', 'movie_director', 'created_by__username']
    ordering = ['-created_at']
    
    def get_vote_score(self, obj):
        return obj.get_vote_score()
    get_vote_score.short_description = 'Vote Score'

class PetitionVoteAdmin(admin.ModelAdmin):
    list_display = ['petition', 'user', 'vote_type', 'created_at']
    list_filter = ['vote_type', 'created_at']
    search_fields = ['petition__movie_title', 'user__username']
    ordering = ['-created_at']

# Register your models here.
admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)
admin.site.register(MoviePetition, MoviePetitionAdmin)
admin.site.register(PetitionVote, PetitionVoteAdmin)