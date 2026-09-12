from django.urls import path
from . import views

app_name = "blog"
urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('create/', views.post_create, name='post_create'),
    path('post/<int:pk>/edit/', views.post_edit, name="post_edit"),
    path(
        "post/<int:pk>/delete/",
        views.post_delete,
        name="post_delete",
    ),
    path(
        "my-posts/",
        views.my_posts,
        name="my_posts",
    ),
    path(
        "comments/",
        views.comment_list,
        name="comment_list",
    ),
    path(
        "contact/",
        views.contact,
        name="contact",
    ),
    path(
        "about/",
        views.about,
        name="about",
    ),
    path(
    "comments/<int:pk>/approve/",
    views.comment_approve,
    name="comment_approve",
    ),

    path(
        "comments/<int:pk>/delete/",
        views.comment_delete,
        name="comment_delete",
    ),
    path(
        "post/<int:pk>/bookmark/",
        views.post_bookmark_toggle,
        name="post_bookmark_toggle",
    ),
    path(
        "bookmarks/",
        views.bookmark_list,
        name="bookmark_list",
    ),
    
    path(
        "post/<int:pk>/like/",
        views.post_like_toggle,
        name="post_like_toggle",
    ),

    path(
        'post/<slug:slug>/',
        views.post_detail, 
        name='post_detail',
    ),
    path(
        'category/<slug:slug>/', 
        views.category_posts, 
        name='category_posts',
    ),
    path(
        'tag/<slug:slug>/', 
        views.tag_posts, 
        name='tag_posts',
    ),
    path(
        'search/', 
        views.search_posts, 
        name='search_posts',
    ),
    
]
