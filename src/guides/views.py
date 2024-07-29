from django.shortcuts import render, get_object_or_404
from .models import Section, Guide, Feedback
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import json
from django.db.models import Prefetch


@require_http_methods(["POST"])
def feedback(request, guide):
    upvote = json.loads(request.body).get("upvote", False)

    guide = get_object_or_404(Guide, slug=guide)

    feedback, created = Feedback.objects.get_or_create(guide=guide, user=request.user, defaults={"upvote": upvote})

    if feedback.upvote == upvote and not created:
        feedback.delete()
    else:
        feedback.upvote = upvote
        feedback.save()

    return JsonResponse({"upvote": feedback.upvote})


def index(request):
    # Get all categories and guides for the sidebar table of contents
    # sections = Section.objects.all().prefetch_related("guide_set").only("id", "slug", "name")
    sections = (
        Section.objects.all().order_by("-id").prefetch_related(Prefetch("guide_set", Guide.objects.all().order_by("id")))
    )
    context = {
        "sections": sections,
    }

    return render(request, "guides/docs.html", context)


def guide_detail(request, guide):
    guide = get_object_or_404(Guide, slug=guide)

    try:
        feedback = Feedback.objects.get(guide=guide, user=request.user)
        guide.upvote = "upvote" if feedback.upvote else "downvote"
    except Exception:
        guide.upvote = "none"

    # Get all categories and guides for the sidebar table of contents
    sections = (
        Section.objects.all()
        .order_by("-id")
        .prefetch_related(Prefetch("guide_set", Guide.objects.all().order_by("id")))
    )
    # sections = Section.objects.all().prefetch_related("guide_set").only("id", "slug", "name")

    context = {
        "guide": guide,
        "sections": sections,
    }

    return render(request, "guides/guide_detail.html", context)
