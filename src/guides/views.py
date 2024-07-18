from django.shortcuts import render, get_object_or_404
from .models import Section, Guide, Feedback
from django.views.decorators.http import require_http_methods
from django.contrib import messages


@require_http_methods(["POST"])
def toggle_status(request, guide):
    upvote = bool(request.POST.get("upvote"))

    guide = get_object_or_404(Guide, slug=guide)

    feedback, _ = Feedback.objects.get_or_create(guide=guide, user=request.user)

    feedback.upvote = upvote
    feedback.save()

    messages.success(request, "Your feedback has been sent")

    context = {"feedback": feedback}

    return render(request, "guides/components/feedback.html", context)


def index(request):
    # Get all categories and guides for the sidebar table of contents
    sections = Section.objects.all().prefetch_related("guide_set").only("id", "slug", "name")

    context = {
        "sections": sections,
    }

    return render(request, "guides/docs.html", context)


def guide_detail(request, guide):
    # Get the category and guide based on slugs
    guide = get_object_or_404(Guide, slug=guide)

    # Get all categories and guides for the sidebar table of contents
    sections = Section.objects.all().prefetch_related("guide_set").only("id", "slug", "name")

    context = {
        "guide": guide,
        "sections": sections,
    }

    return render(request, "guides/guide_detail.html", context)
