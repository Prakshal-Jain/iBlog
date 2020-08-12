from django.shortcuts import render, redirect, get_object_or_404
from .forms import PostForm, CommentForm
# Create your views here.
from django.views import generic
from .models import Post, Comment
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.decorators import login_required

class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    template_name = 'home.html'

class myPosts(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    template_name = 'myPosts.html'

class DraftList(generic.ListView):
    queryset = Post.objects.filter(status=0).order_by('-created_on')
    template_name = 'drafts.html'


class PostDetail(generic.DetailView):
    model = Post
    template_name = 'post_detail.html'


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.created_on = timezone.now()
            post.save()
            if form.cleaned_data['status'] == 1:
                send_mail(
                    'A new post is added to the Website with ID ' + str(post.pk),
                    str("Title: " + form.cleaned_data['title'] + "\n\n" + "Author: " + str(request.user.username) + "\n\n" + "Description: " + form.cleaned_data['content']),
                    settings.EMAIL_HOST_USER,
                    ['prakshal@buffalo.edu'],
                    fail_silently=False,
                )
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'post_edit.html', {'form': form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.updated_on = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'post_edit.html', {'form': form})


def delete_post(request, pk):
    b = Post.objects.get(id=pk)
    b.delete()
    return redirect('/', pk=pk)

def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'add_comment_to_post.html', {'form': form})

@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('post_detail', pk=comment.post.pk)