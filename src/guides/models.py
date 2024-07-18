from django.db import models
from django.contrib.auth.models import User


class Section(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Guide(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()

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
