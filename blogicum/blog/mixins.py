from django.urls import reverse_lazy


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
