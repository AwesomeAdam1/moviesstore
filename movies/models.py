from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')
    def __str__(self):
        return str(self.id) + ' - ' + self.name
class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie,
        on_delete=models.CASCADE)
    user = models.ForeignKey(User,
        on_delete=models.CASCADE)
    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name
class HiddenMovie(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,
        on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie,
        on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = (('user', 'movie'),)
    def __str__(self):
        return f"Hidden: {self.user.username} -> {self.movie.name}"

class MoviePetition(models.Model):
    id = models.AutoField(primary_key=True)
    movie_title = models.CharField(max_length=255)
    movie_description = models.TextField(blank=True, null=True)
    movie_year = models.IntegerField(blank=True, null=True)
    movie_director = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')
    
    def __str__(self):
        return f"Petition: {self.movie_title} by {self.created_by.username}"
    
    def get_vote_score(self):
        upvotes = self.petitionvote_set.filter(vote_type='upvote').count()
        downvotes = self.petitionvote_set.filter(vote_type='downvote').count()
        return upvotes - downvotes
    
    def get_upvotes(self):
        return self.petitionvote_set.filter(vote_type='upvote').count()
    
    def get_downvotes(self):
        return self.petitionvote_set.filter(vote_type='downvote').count()

class PetitionVote(models.Model):
    VOTE_TYPES = [
        ('upvote', 'Upvote'),
        ('downvote', 'Downvote'),
    ]
    
    id = models.AutoField(primary_key=True)
    petition = models.ForeignKey(MoviePetition, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=10, choices=VOTE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = (('petition', 'user'),)
    
    def __str__(self):
        return f"{self.user.username} {self.vote_type} on {self.petition.movie_title}"