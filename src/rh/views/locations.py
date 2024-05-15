from django.contrib.auth.decorators import login_required

from django.http import JsonResponse

from ..models import (
    Location,
)


@login_required
def load_locations_details(request):
    parent_ids = [int(i) for i in request.POST.getlist("parents[]") if i]
    parents = Location.objects.filter(pk__in=parent_ids).select_related("parent")

    response = "".join(
        [
            f'<optgroup label="{parent.name}">'
            + "".join(
                [f'<option value="{location.pk}">{location}</option>' for location in parent.children.order_by("name")]
            )
            + "</optgroup>"
            if parent.children.exists()
            else ""
            for parent in parents
        ]
    )

    return JsonResponse(response, safe=False)

