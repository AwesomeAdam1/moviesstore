from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, HiddenMovie
from django.contrib.auth.decorators import login_required

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