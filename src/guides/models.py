from django.db import models
from django.contrib.auth.models import User
from mdeditor.fields import MDTextField


class Section(models.Model):
    name = models.CharField(max_length=255,null=False)
    slug = models.SlugField(unique=True,null=False)

    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Guide(models.Model):
    section = models.ForeignKey(Section, on_delete=models.SET_NULL,null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL,null=True)

    title = models.CharField(max_length=512,null=False)
    slug = models.SlugField(unique=True,null=False)
    content = MDTextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Feedback(models.Model):
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    upvote = models.BooleanField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("guide", "user")

    def __str__(self):
        return f"{'Upvote' if self.upvote else 'Downvote'} by {self.user.username} on {self.guide.title}"
