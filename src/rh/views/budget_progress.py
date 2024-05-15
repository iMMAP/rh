from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render


from ..forms import (
    BudgetProgressForm,
)
from ..models import (
    BudgetProgress,
    Project,
)

#############################################
########## Budget Progress Views ############
#############################################



@login_required
def create_project_budget_progress_view(request, project):
    project = get_object_or_404(Project, pk=project)

    budget_progress = project.budgetprogress_set.all()

    BudgetProgressFormSet = modelformset_factory(BudgetProgress, form=BudgetProgressForm, extra=1)
    formset = BudgetProgressFormSet(request.POST or None, queryset=budget_progress, form_kwargs={"project": project})

    if request.method == "POST":
        country = request.POST.get("country")

        if formset.is_valid():
            for form in formset:
                if form.cleaned_data.get("save"):
                    if form.cleaned_data.get("activity_domain") and form.cleaned_data.get("donor"):
                        budget_progress = form.save(commit=False)
                        budget_progress.project = project
                        budget_progress.country_id = country
                        budget_progress.title = f"{budget_progress.donor}: {budget_progress.activity_domain}"
                        budget_progress.save()
            return redirect("create_project_budget_progress", project=project.pk)
        else:
            for form in formset:
                for error in form.errors:
                    error_message = f"Something went wrong {formset.errors}"
                    if form.errors[error]:
                        error_message = f"{error}: {form.errors[error][0]}"
                    messages.error(request, error_message)

    # progress = list(budget_progress.values_list("pk", flat=True))

    context = {
        "project": project,
        "formset": formset,
        "project_view": False,
        "financial_view": True,
        "reports_view": False,
    }
    return render(request, "rh/financial_reports/project_budget_progress.html", context)



@login_required
def copy_budget_progress(request, project, budget):
    project = get_object_or_404(Project, pk=project)
    budget_progress = get_object_or_404(BudgetProgress, pk=budget)
    new_budget_progress = get_object_or_404(BudgetProgress, pk=budget_progress.pk)
    if new_budget_progress:
        new_budget_progress.pk = None
        new_budget_progress.save()
        new_budget_progress.project = project
        new_budget_progress.active = True
        new_budget_progress.state = "draft"
        new_budget_progress.title = f"[COPY] - {budget_progress.title}"
        new_budget_progress.save()
    return JsonResponse({"success": True})



@login_required
def delete_budget_progress(request, pk):
    budget_progress = get_object_or_404(BudgetProgress, pk=pk)
    # project = budget_progress.project
    if budget_progress:
        budget_progress.delete()
    return JsonResponse({"success": True})