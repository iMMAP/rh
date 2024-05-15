from django.contrib.auth.decorators import login_required
from django.http import  JsonResponse
from django.template.loader import render_to_string

from ..forms import (
    DisaggregationFormSet,
)
from ..models import (
    Indicator,
)


@login_required
def get_disaggregations_forms(request):
    """Get target location empty form"""
    # Get selected indicators
    indicator = Indicator.objects.get(pk=request.POST.get("indicator"))
    locations_prefix = request.POST.getlist("locations_prefixes[]")

    related_disaggregations = indicator.disaggregation_set.all()

    location_disaggregation_dict = {}

    initial_data = []

    # Populate initial data with related disaggregations
    if len(related_disaggregations) > 0:
        for disaggregation in related_disaggregations:
            initial_data.append({"disaggregation": disaggregation})

        # Create DisaggregationFormSet for each location prefix
        for location_prefix in locations_prefix:
            # Check if is from the add new form or from the activity create
            DisaggregationFormSet.max_num = len(related_disaggregations)
            DisaggregationFormSet.extra = len(related_disaggregations)

            disaggregation_formset = DisaggregationFormSet(
                prefix=f"disaggregation_{location_prefix}", initial=initial_data
            )

            for disaggregation_form in disaggregation_formset.forms:
                # disaggregation_form = modelform_factory(DisaggregationLocation,fields=["target","disaggregation"])
                context = {
                    "disaggregation_form": disaggregation_form,
                }

                html = render_to_string("rh/projects/forms/disaggregation_empty_form.html", context)

                if location_prefix in location_disaggregation_dict:
                    location_disaggregation_dict[location_prefix].append(html)
                else:
                    location_disaggregation_dict.update({location_prefix: [html]})

    # Set back extra to 0 to avoid empty forms if refreshed.

    # Return JSON response containing generated HTML forms
    return JsonResponse(location_disaggregation_dict)




