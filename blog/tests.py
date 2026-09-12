from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.models import Profile

from .models import Category, Post, Tag


User = get_user_model()


@override_settings(
    ALLOWED_HOSTS=[
        "testserver",
        "127.0.0.1",
        "localhost",
    ]
)
class BlogCoreTests(TestCase):

    def setUp(self):
        self.author = User.objects.create_user(
            username="writer",
            email="writer@example.com",
            password="testpass12345",
        )

        self.reader = User.objects.create_user(
            username="reader",
            email="reader@example.com",
            password="testpass12345",
        )

        Profile.objects.get_or_create(
            user=self.author,
        )

        Profile.objects.get_or_create(
            user=self.reader,
        )

        self.category = Category.objects.create(
            name="Django",
            slug="django",
        )

        self.tag = Tag.objects.create(
            name="Python",
            slug="python",
        )

        self.post = Post.objects.create(
            title="Public Post",
            slug="public-post",
            author=self.author,
            category=self.category,
            excerpt="This is a public post excerpt.",
            body="<p>This is the public post body about Django and Python.</p>",
            status=Post.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        self.post.tags.add(
            self.tag,
        )

        self.draft = Post.objects.create(
            title="Draft Post",
            slug="draft-post",
            author=self.author,
            category=self.category,
            excerpt="This is a draft post excerpt.",
            body="<p>This is a draft post body.</p>",
            status=Post.Status.DRAFT,
            published_at=None,
        )

    def test_homepage_loads_published_posts_only(self):
        response = self.client.get(
            reverse("blog:post_list"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Public Post",
        )

        self.assertNotContains(
            response,
            "Draft Post",
        )

    def test_post_detail_loads_and_increments_view_count(self):
        old_view_count = self.post.view_count

        response = self.client.get(
            reverse(
                "blog:post_detail",
                kwargs={
                    "slug": self.post.slug,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            self.post.title,
        )

        self.post.refresh_from_db()

        self.assertEqual(
            self.post.view_count,
            old_view_count + 1,
        )

    def test_draft_post_detail_returns_404(self):
        response = self.client.get(
            reverse(
                "blog:post_detail",
                kwargs={
                    "slug": self.draft.slug,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_category_page_loads(self):
        response = self.client.get(
            reverse(
                "blog:category_posts",
                kwargs={
                    "slug": self.category.slug,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            self.post.title,
        )

    def test_tag_page_loads(self):
        response = self.client.get(
            reverse(
                "blog:tag_posts",
                kwargs={
                    "slug": self.tag.slug,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            self.post.title,
        )

    def test_search_page_finds_matching_post(self):
        response = self.client.get(
            reverse("blog:search_posts"),
            {
                "q": "Django",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            self.post.title,
        )

    def test_about_page_loads(self):
        response = self.client.get(
            reverse("blog:about"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_contact_page_loads(self):
        response = self.client.get(
            reverse("blog:contact"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_contact_form_post_redirects_after_success(self):
        response = self.client.post(
            reverse("blog:contact"),
            {
                "name": "Test User",
                "email": "test@example.com",
                "subject": "Testing Contact Form",
                "message": "This is a test message.",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_bookmark_toggle_adds_and_removes_bookmark(self):
        self.client.force_login(
            self.reader,
        )

        url = reverse(
            "blog:post_bookmark_toggle",
            kwargs={
                "pk": self.post.pk,
            },
        )

        self.client.post(
            url,
            {
                "next": self.post.get_absolute_url(),
            },
        )

        self.assertTrue(
            self.post.bookmarks.filter(
                pk=self.reader.pk,
            ).exists()
        )

        self.client.post(
            url,
            {
                "next": self.post.get_absolute_url(),
            },
        )

        self.assertFalse(
            self.post.bookmarks.filter(
                pk=self.reader.pk,
            ).exists()
        )

    def test_bookmark_list_shows_saved_post(self):
        self.client.force_login(
            self.reader,
        )

        self.post.bookmarks.add(
            self.reader,
        )

        response = self.client.get(
            reverse("blog:bookmark_list"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            self.post.title,
        )

    def test_like_toggle_adds_and_removes_like(self):
        self.client.force_login(
            self.reader,
        )

        url = reverse(
            "blog:post_like_toggle",
            kwargs={
                "pk": self.post.pk,
            },
        )

        self.client.post(
            url,
            {
                "next": self.post.get_absolute_url(),
            },
        )

        self.assertTrue(
            self.post.likes.filter(
                pk=self.reader.pk,
            ).exists()
        )

        self.client.post(
            url,
            {
                "next": self.post.get_absolute_url(),
            },
        )

        self.assertFalse(
            self.post.likes.filter(
                pk=self.reader.pk,
            ).exists()
        )

    def test_sitemap_loads(self):
        response = self.client.get(
            "/sitemap.xml",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            b"<urlset",
            response.content,
        )

        self.assertIn(
            b"public-post",
            response.content,
        )

    def test_robots_txt_loads(self):
        response = self.client.get(
            "/robots.txt",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "User-agent: *",
        )

        self.assertContains(
            response,
            "Sitemap:",
        )