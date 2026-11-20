from django.urls import path

from . import views

app_name = 'blogs'
urlpatterns = [
    path('', views.index, name='index'),
    path('posts/new/', views.post_create, name='create'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='edit'),
]