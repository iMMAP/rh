from django.test import TestCase
from django.urls import reverse
from .factory import  SectionFactory, GuideFactory, FeedbackFactory
from django.contrib.auth.models import User


class ViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.section = SectionFactory()
        self.guide = GuideFactory(section=self.section,author=self.user)
        self.feedback = FeedbackFactory(guide=self.guide, user=self.user, upvote=True)

    def test_index_view(self):
        response = self.client.get(reverse("docs"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "guides/docs.html")

    def test_guide_detail_view(self):
        response = self.client.get(reverse("guides-detail", args=[self.guide.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "guides/guide_detail.html")
        self.assertTrue('sections' in response.context)
        self.assertTrue('guide' in response.context)
    
    def test_feedback_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse("guides-feedback", args=[self.guide.slug]), {"upvote": False}, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["upvote"], False)