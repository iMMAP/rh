from django.contrib import admin
from .models import Section, Guide, Feedback


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "description")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ["name"]}


@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    list_display = (
        "section",
        "author",
        "title",
        "slug",
        "feedbacks",
        "created_at",
        "updated_at",
    )
    list_filter = ("section", "created_at", "updated_at")
    search_fields = ("slug",)
    date_hierarchy = "created_at"
    prepopulated_fields = {"slug": ["title"]}

    def feedbacks(self, obj):
        return f"Upvote: {obj.feedback_set.filter(upvote=True).count()} - Downvote: {obj.feedback_set.filter(upvote=False).count()}"


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("guide", "user", "upvote", "created_at")
    list_filter = ("upvote", "created_at")
    date_hierarchy = "created_at"
