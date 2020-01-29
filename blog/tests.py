
import pytest

from django.test import TestCase
from django.urls import reverse

from .models import Post, Comment
from django.contrib.auth.models import User


class PostTests(TestCase):

    def setUp(self):
        self.username = 'username'
        self.password = 'password'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_user(self):
        assert len(User.objects.all()) == 1

    def test_drafts_redirect(self):
        resp = self.client.get(reverse('post_draft_list'))
        assert resp.status_code == 302
        assert reverse('login') in resp.url
        assert reverse('post_draft_list') in resp.url

    def test_no_posts(self):
        posts = Post.objects.all()
        self.assertRedirects
        assert len(posts) == 0

    def login(self):
        resp = self.client.post(reverse('login'), data={'username': self.username, 'password': self.password})
        assert resp.status_code == 302
        assert '_auth_user_id' in self.client.session
        assert reverse('post_list') in resp.url

    def test_posts(self):
        self.login()

        resp = self.client.get(reverse('post_new'))
        assert resp.status_code == 200
        resp = self.client.post(reverse('post_new'), data={'title': 'title 1', 'text': 'text 1'})
        assert resp.status_code == 302
        assert reverse('login') not in resp.url
        self.client.post(reverse('post_new'), data={'title': 'title 2', 'text': 'text 2'})
        assert len(Post.objects.all()) == 2
        post1, post2 = Post.objects.all()

        resp = self.client.get(reverse('post_draft_list'))
        self.assertContains(resp, post1.title)
        self.assertContains(resp, post2.title)

        resp = self.client.get(reverse('post_publish', args=(post1.pk,)))
        self.assertRedirects(resp, reverse('post_detail', args=(post1.pk,)))
        self.client.get(reverse('post_publish', args=(post2.pk,)))
        resp = self.client.get(reverse('post_list'))
        self.assertContains(resp, post1.title)
        self.assertContains(resp, post2.title)

        resp = self.client.get(reverse('post_draft_list'))
        self.assertNotContains(resp, post1.title)
        self.assertNotContains(resp, post2.title)

        resp = self.client.post(reverse('post_remove', args=(post2.pk,)), follow=True)
        self.assertRedirects(resp, reverse('post_list'))
        self.assertContains(resp, post1.title)
        self.assertNotContains(resp, post2.title)

        resp = self.client.get(reverse('post_edit', args=(post1.pk,)))
        assert resp.status_code == 200
        edited_title = 'edited title 1'
        resp = self.client.post(reverse('post_edit', args=(post1.pk,)), data={'title': edited_title, 'text': post1.text}, follow=True)
        import ipdb; ipdb.set_trace()
        self.assertRedirects(resp, reverse('post_detail', args=(post1.pk,)))
        self.assertContains(resp, edited_title)


    def test_comments(self):
        self.login()

        resp = self.client.post(reverse('post_new'), data={'title': 'title', 'text': 'text'})
        assert resp.status_code == 302
        assert reverse('login') not in resp.url
        assert len(Post.objects.all()) == 1
        post = Post.objects.first()

        resp = self.client.get(reverse('add_comment_to_post', args=(post.pk,)))
        assert resp.status_code == 200
        self.client.post(reverse('add_comment_to_post', args=(post.pk,)), data={'author': 'author 1', 'text': 'text 1'})
        self.client.post(reverse('add_comment_to_post', args=(post.pk,)), data={'author': 'author 2', 'text': 'text 2'})
        comment1, comment2 = Comment.objects.all()

        self.client.logout()
        resp = self.client.get(reverse('post_detail', args=(post.pk,)))
        self.assertNotContains(resp, comment1.text)
        self.assertNotContains(resp, comment2.text)

        self.login()
        resp = self.client.get(reverse('post_detail', args=(post.pk,)))
        self.assertContains(resp, comment1.text)
        self.assertContains(resp, comment2.text)

        resp = self.client.get(reverse('comment_approve', args=(comment1.pk,)))
        self.assertRedirects(resp, reverse('post_detail', args=(post.pk,)))
        self.client.get(reverse('comment_approve', args=(comment2.pk,)))
        self.client.logout()
        resp = self.client.get(reverse('post_detail', args=(post.pk,)))
        self.assertContains(resp, comment1.text)
        self.assertContains(resp, comment2.text)

        self.login()
        resp = self.client.post(reverse('comment_remove', args=(comment2.pk,)), follow=True)
        self.assertRedirects(resp, reverse('post_detail', args=(post.pk,)))
        self.assertContains(resp, comment1.text)
        self.assertNotContains(resp, comment2.text)
