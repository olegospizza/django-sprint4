from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone 
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .forms import UserEditForm, PostForm, CommentForm
from .models import Category, Post, Comment
from .utils import get_published_posts

POSTS_IN_PAGE = 10


class RedirectToUserProfileMixin:
    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={
            'username': self.request.user.username
        })


class RedirectToPostDetailMixin:
    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={
            'post_id': self.get_object().post.id
        })


def annotate_posts(queryset):
    return queryset.annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


def paginate_queryset(request, queryset, per_page=POSTS_IN_PAGE):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    post_list = annotate_posts(get_published_posts())
    page_obj = paginate_queryset(request, post_list)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    is_author = post.author == request.user

    if (
        not post.is_published
        or not post.category.is_published
        or not post.location.is_published
        or post.pub_date > timezone.now()
    ) and not is_author:
        raise Http404

    comments = post.comments.select_related('author').order_by('created_at')
    comment_form = CommentForm()
    return render(request, 'blog/detail.html', {
        'post': post,
        'comments': comments,
        'form': comment_form,
    })


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = annotate_posts(get_published_posts().filter(category=category))
    page_obj = paginate_queryset(request, post_list)
    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': page_obj
    })


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    if request.user == profile_user:
        post_list = annotate_posts(Post.objects.filter(author=profile_user))
    else:
        post_list = annotate_posts(
            get_published_posts().filter(author=profile_user)
        )

    page_obj = paginate_queryset(request, post_list)
    return render(request, 'blog/profile.html', {
        'profile': profile_user,
        'page_obj': page_obj
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('blog:post_detail', post_id=post_id)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def test_func(self):
        return self.request.user == self.get_object().author

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.id})


class UserUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    RedirectToUserProfileMixin,
    UpdateView
):
    model = User
    form_class = UserEditForm
    template_name = 'blog/user.html'

    def test_func(self):
        return self.request.user == self.get_object()

    def get_object(self, queryset=None):
        return self.request.user


class PostCreateView(
    LoginRequiredMixin,
    RedirectToUserProfileMixin,
    CreateView
):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.pub_date = timezone.now()
        return super().form_valid(form)


class PostDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    RedirectToUserProfileMixin,
    DeleteView
):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def test_func(self):
        return self.request.user == self.get_object().author


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        return self.request.user == self.get_object().author

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={
            'post_id': self.get_object().post.id
        })


class CommentDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    RedirectToPostDetailMixin,
    DeleteView
):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        return self.request.user == self.get_object().author
