from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from blog.models import Post, Comment
from blog.forms import PostForm, CommentForm


def index(request):
    if request.GET:
        data = request.GET
        search = data['search_box']
        list_post = [post for post in Post.objects.all() if search in post.theme]
    else:
        list_post = Post.objects.all()[:10]
        search = None
    context = {'list_post':list_post, 'search':search}
    return render(request, 'index.html', context)

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = Comment.objects.filter(post=pk)
    comments = comments.order_by('creation_date').reverse()
    return render(request, 'post_detail.html', {'post': post, 'comments': comments})

def post_add(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'post_add.html', {'form':form})

def comment_add(request, pk):
    print(request.POST)
    post = get_object_or_404(Post, pk=pk)
    print(post)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'comment_add.html', {'form':form})