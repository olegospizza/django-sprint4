"""
URL configuration for blogicum project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from .views import CustomLogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/logout/', CustomLogoutView.as_view(), name="logout"),
    path('auth/', include('django.contrib.auth.urls')),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('blog:index'),
        ),
        name='registration',
    ),
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
]

handler404 = 'pages.views.page_not_found'
handler403 = 'pages.views.csrf_failure'
handler500 = 'pages.views.server_error'
