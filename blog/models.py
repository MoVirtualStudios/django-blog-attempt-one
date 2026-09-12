from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count

import math
import re


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(
            status=self.model.Status.PUBLISHED,
            published_at__lte=timezone.now(),
        )

    def with_counts(self):
        return self.annotate(
            like_total=Count(
                "likes",
                distinct=True,
             ),
            bookmark_total=Count(
                "bookmarks",
                distinct=True,
            ),
        )


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(
        max_length=120,
        unique=True,
    )
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "blog:category_posts", 
            args=[self.slug]
            )
    

class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(
        max_length=60,
        unique=True,
    )
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "blog:tag_posts",
            args=[self.slug]
            )
    

class Post(models.Model):

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    title = models.CharField(max_length=200)

    slug = models.SlugField(
        max_length=220,
        unique=True
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts"
    )

    excerpt = models.TextField(
        max_length=300,
        blank=True,
    )
    
    body = models.TextField()

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT
    )
    featured_image = models.ImageField(
        upload_to="posts/%Y/%m/",
        blank=True,
    )

    featured_image_alt = models.CharField(
            max_length=255,
            blank=True,
        )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    reading_time = models.PositiveIntegerField(
        default=1,
    )

    view_count = models.PositiveIntegerField(
        default=0,
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    objects = PostQuerySet.as_manager()

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name = "posts",
        null=True,
        blank=True,
    )

    tags = models.ManyToManyField(
        Tag,
        related_name="posts",
        blank=True
    )

    bookmarks = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="bookmarked_posts",
        blank=True,
    )

    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="liked_posts",
        blank=True,
    )
    
    class Meta:
        ordering = ["-published_at", "-created_at"]

    def calculate_reading_time(self):
        text = re.sub(r"<[^>]+>", "", self.body)
        words = len(text.split())
        return max(1, math.ceil(words / 200),)

    def save(self, *args, **kwargs):
        self.reading_time = self.calculate_reading_time()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            "blog:post_detail",
            args=[self.slug]
        )


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments",
    )

    name = models.CharField( max_length=100,)
    email = models.EmailField()
    body = models.TextField()
    created_at = models.DateTimeField( auto_now_add=True,)
    approved = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.name} on {self.post}"