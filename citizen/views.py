from django.shortcuts import render, redirect
from .models import Post, status, Vote
from .forms import PostForm, UserRegistrationForm, LoginForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce

# Create your views here.

def loginPage(request):
    # Check if there's a next parameter in the URL or form submission
    next_url = request.GET.get('next', '')
    if not next_url:
        next_url = request.POST.get('next', '')

    # If next_url is empty or not provided, default to home
    if not next_url:
        next_url = 'home'

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                # Check if next_url is a full URL or just a path
                if next_url == 'home' or next_url.startswith('/'):
                    return redirect(next_url)
                else:
                    # If it's not a valid URL pattern, default to home
                    return redirect('home')
            else:
                messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = LoginForm()

    return render(request, 'citizen/login.html', {'form': form, 'next': next_url})

def registerPage(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'citizen/register.html', {'form': form})


def logoutUser(request):
    logout(request)
    return redirect('home')

@login_required(login_url='login')
def grevance(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your grievance has been submitted successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill the host field with the current user
        initial_data = {'host': request.user}
        form = PostForm(initial=initial_data)

    context = {'form': form}
    return render(request, 'citizen/grevance_from.html', context)

@login_required(login_url='login')
def post(request, pk):
    post = get_object_or_404(Post, id=pk)
    # Get user's vote if it exists
    user_vote = None
    if request.user.is_authenticated:
        try:
            user_vote = Vote.objects.get(user=request.user, post=post)
        except Vote.DoesNotExist:
            pass

    context = {
        'post': post,
        'user_vote': user_vote,
        'upvote_count': post.get_upvote_count(),
        'downvote_count': post.get_downvote_count(),
    }
    return render(request, 'citizen/grevance_show.html', context)

def home(request):
    # Annotate posts with vote count and order by vote count (descending)
    # Use Coalesce to handle NULL values (when there are no votes)
    posts = Post.objects.all().annotate(vote_count=Coalesce(Sum('votes__value'), 0)).order_by('-vote_count', '-created')

    # Get user's votes for highlighting in the UI
    user_votes = {}
    if request.user.is_authenticated:
        votes = Vote.objects.filter(user=request.user)
        for vote in votes:
            user_votes[vote.post_id] = vote.value

    context = {
        'posts': posts,
        'user_votes': user_votes
    }
    return render(request, 'citizen/home.html', context)

@login_required(login_url='/login')
def change_status(request, pk):
    post = get_object_or_404(Post, id=pk)
    if request.user.is_staff:
        post.status = status.objects.get(name="Resolved")
        post.save()
        messages.success(request, 'Status updated to resolved.')
    else:
        messages.error(request, 'You do not have permission to change the status.')
    return redirect('view_grevance', pk=pk)

@login_required(login_url='login')
def vote_post(request, pk, vote_type):
    post = get_object_or_404(Post, id=pk)

    # Check if user has already voted
    try:
        vote = Vote.objects.get(user=request.user, post=post)
        # If vote exists, update it
        if vote_type == 'upvote':
            if vote.value == 1:  # Already upvoted, remove vote
                vote.delete()
            else:  # Change to upvote
                vote.value = 1
                vote.save()
        elif vote_type == 'downvote':
            if vote.value == -1:  # Already downvoted, remove vote
                vote.delete()
            else:  # Change to downvote
                vote.value = -1
                vote.save()
    except Vote.DoesNotExist:
        # Create new vote
        if vote_type == 'upvote':
            Vote.objects.create(user=request.user, post=post, value=1)
        elif vote_type == 'downvote':
            Vote.objects.create(user=request.user, post=post, value=-1)

    # Return JSON response for AJAX or redirect for non-AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'upvote_count': post.get_upvote_count(),
            'downvote_count': post.get_downvote_count(),
            'total_votes': post.get_vote_count()
        })
    else:
        return HttpResponseRedirect(reverse('view_grevance', args=[pk]))

@login_required(login_url='login')
def my_complaints(request):
    # Get all complaints by the current user and sort by vote count
    # Use Coalesce to handle NULL values (when there are no votes)
    posts = Post.objects.filter(host=request.user).annotate(vote_count=Coalesce(Sum('votes__value'), 0)).order_by('-vote_count', '-created')

    # Get user's votes for highlighting in the UI
    user_votes = {}
    votes = Vote.objects.filter(user=request.user)
    for vote in votes:
        user_votes[vote.post_id] = vote.value

    context = {
        'posts': posts,
        'user_votes': user_votes
    }
    return render(request, 'citizen/my_complaints.html', context)

@login_required(login_url='login')
def edit_complaint(request, pk):
    post = get_object_or_404(Post, id=pk)

    # Check if the user is the owner of the complaint
    if post.host != request.user:
        messages.error(request, "You don't have permission to edit this complaint.")
        return redirect('my_complaints')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your complaint has been updated successfully!')
            return redirect('my_complaints')
    else:
        form = PostForm(instance=post)

    context = {'form': form, 'post': post}
    return render(request, 'citizen/edit_complaint.html', context)

@login_required(login_url='login')
def delete_complaint(request, pk):
    post = get_object_or_404(Post, id=pk)

    # Check if the user is the owner of the complaint
    if post.host != request.user:
        messages.error(request, "You don't have permission to delete this complaint.")
        return redirect('my_complaints')

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Your complaint has been deleted successfully!')
        return redirect('my_complaints')

    context = {'post': post}
    return render(request, 'citizen/delete_complaint.html', context)

