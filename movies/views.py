from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, HiddenMovie, MoviePetition, PetitionVote
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

# Create your views here.
def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies_qs = Movie.objects.filter(name__icontains=search_term)
    else:
        movies_qs = Movie.objects.all()
    if request.user.is_authenticated:
        hidden_ids = HiddenMovie.objects.filter(user=request.user).values_list('movie_id', flat=True)
        movies_qs = movies_qs.exclude(id__in=list(hidden_ids))
    movies = movies_qs
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html',
                  {'template_data': template_data})
def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html',
                  {'template_data': template_data})
@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html',
            {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id,
        user=request.user)
    review.delete()
    return redirect('movies.show', id=id)
@login_required
def hide(request, id):
    if request.method == 'POST':
        movie = get_object_or_404(Movie, id=id)
        HiddenMovie.objects.get_or_create(user=request.user, movie=movie)
    return redirect('movies.index')
@login_required
def unhide(request, id):
    if request.method == 'POST':
        movie = get_object_or_404(Movie, id=id)
        HiddenMovie.objects.filter(user=request.user, movie=movie).delete()
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('movies.index')
@login_required
def hidden(request):
    hidden_entries = HiddenMovie.objects.filter(user=request.user).select_related('movie').order_by('-created_at')
    movies = [hm.movie for hm in hidden_entries]
    template_data = {}
    template_data['title'] = 'Hidden Movies'
    template_data['movies'] = movies
    return render(request, 'movies/hidden.html', {'template_data': template_data})

# Petition views
def petitions(request):
    petitions = MoviePetition.objects.all().order_by('-created_at')
    template_data = {}
    template_data['title'] = 'Movie Petitions'
    template_data['petitions'] = petitions
    return render(request, 'movies/petitions.html', {'template_data': template_data})

@login_required
def create_petition(request):
    if request.method == 'POST':
        movie_title = request.POST.get('movie_title')
        movie_description = request.POST.get('movie_description', '')
        movie_year = request.POST.get('movie_year')
        movie_director = request.POST.get('movie_director', '')
        
        if movie_title:
            petition = MoviePetition(
                movie_title=movie_title,
                movie_description=movie_description,
                movie_year=int(movie_year) if movie_year else None,
                movie_director=movie_director,
                created_by=request.user
            )
            petition.save()
            messages.success(request, 'Your movie petition has been created successfully!')
            return redirect('movies.petitions')
        else:
            messages.error(request, 'Movie title is required.')
    
    template_data = {}
    template_data['title'] = 'Create Movie Petition'
    return render(request, 'movies/create_petition.html', {'template_data': template_data})

def petition_detail(request, id):
    petition = get_object_or_404(MoviePetition, id=id)
    user_vote = None
    if request.user.is_authenticated:
        try:
            user_vote = PetitionVote.objects.get(petition=petition, user=request.user)
        except PetitionVote.DoesNotExist:
            pass
    
    template_data = {}
    template_data['title'] = f'Petition: {petition.movie_title}'
    template_data['petition'] = petition
    template_data['user_vote'] = user_vote
    template_data['vote_score'] = petition.get_vote_score()
    template_data['upvotes'] = petition.get_upvotes()
    template_data['downvotes'] = petition.get_downvotes()
    return render(request, 'movies/petition_detail.html', {'template_data': template_data})

@login_required
def vote_petition(request, id):
    if request.method == 'POST':
        petition = get_object_or_404(MoviePetition, id=id)
        vote_type = request.POST.get('vote_type')
        
        if vote_type in ['upvote', 'downvote']:
            # Check if user already voted
            existing_vote, created = PetitionVote.objects.get_or_create(
                petition=petition,
                user=request.user,
                defaults={'vote_type': vote_type}
            )
            
            if not created:
                # User already voted, update or remove vote
                if existing_vote.vote_type == vote_type:
                    # Same vote, remove it
                    existing_vote.delete()
                    messages.info(request, 'Your vote has been removed.')
                else:
                    # Different vote, update it
                    existing_vote.vote_type = vote_type
                    existing_vote.save()
                    messages.success(request, f'Your vote has been changed to {vote_type}.')
            else:
                messages.success(request, f'Your {vote_type} has been recorded.')
        
        return redirect('movies.petition_detail', id=id)
    
    return redirect('movies.petitions')