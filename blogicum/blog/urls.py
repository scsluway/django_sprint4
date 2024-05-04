from django.urls import path, include

from . import views

app_name = 'blog'


post_urls = [
    path('<int:post_id>/', views.post_detail, name='post_detail'),
    path('create/', views.PostCreateView.as_view(), name='create_post'),
    path(
        '<int:post_id>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        '<int:post_id>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),
    path(
        '<int:post_id>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment'
    ),
    path(
        '<int:post_id>/edit_comment/<int:comment_id>/',
        views.CommentUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        '<int:post_id>/delete_comment/<int:comment_id>/',
        views.CommentDeleteView.as_view(),
        name='delete_comment'
    ),
]

profile_urls = [
    path(
        'edit/',
        views.ProfileUpdateView.as_view(),
        name='edit_profile'
    ),
    path(
        '<str:username>/',
        views.ProfileListView.as_view(),
        name='profile'
    ),
]


urlpatterns = [
    path('', views.index, name='index'),
    path('category/<slug:category_slug>/',
         views.category_posts, name='category_posts'),
    path('posts/', include(post_urls)),
    path('profile/', include(profile_urls)),
]
