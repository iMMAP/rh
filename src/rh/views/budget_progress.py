from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
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
    financial_report = project.budgetprogress_set.all()
    
    if request.method == "POST":
        form = BudgetProgressForm(request.POST, project=project)
        country = request.POST.get("country")
        if form.is_valid():
            budget_progress = form.save(commit=False)
            activity_domain_ids = request.POST.getlist("activity_domains")
            budget_progress.project = project
            budget_progress.country_id = country

            budget_progress.save()
            budget_progress.activity_domains.set(activity_domain_ids)
            activity_domain_names = f"{', '.join([str(ad) for ad in budget_progress.activity_domains.all()])}"
            budget_progress.title = f"{budget_progress.donor}: {activity_domain_names}"
            budget_progress.save()

            messages.success(request, f"Financial Report for {budget_progress.donor} has been saved successfully.")
            return redirect("create_project_budget_progress", project=project.pk)
        else:
            messages.error(request, "Something went wrong. Please fix the below errors.")
            return redirect("create_project_budget_progress", project=project.pk)
    else:
        form = BudgetProgressForm(project=project)

    total_budget = financial_report.aggregate(total_budget=Sum("amount_recieved", default=0))["total_budget"]
    calc = {
        "extended_budget": max(total_budget - project.budget, 0),
        "budget_gap": max(project.budget - total_budget, 0),
        "total_budget": total_budget,
    }

    donor_names = []
    donor_funds = []
    activity_funds = []
    activity_names = []
    donor_names_funds = {}
    activity_names_funds = {}
    if financial_report.exists():
        for data in financial_report:
            if data.donor.name not in donor_names_funds.keys():
                donor_names_funds[data.donor.name] = data.amount_recieved
            else:
                donor_names_funds[data.donor.name] += data.amount_recieved

            activities = " | ".join([str(ad) for ad in data.activity_domains.all()])

            if activities not in activity_names_funds.keys():
                activity_names_funds[activities] = data.amount_recieved
            else:
                activity_names_funds[activities] += data.amount_recieved
        for names, funds in activity_names_funds.items():
            activity_funds.append(funds)
            activity_names.append(names)
        for donor, fund in donor_names_funds.items():
            donor_names.append(donor)
            donor_funds.append(fund)

    context = {
        "project": project,
        "budget_progress": financial_report,
        "calc": calc,
        "form": form,
        "donor_names": list(donor_names),
        "donor_funds": list(donor_funds),
        "activity_names": list(activity_names),
        "activity_funds": list(activity_funds),
        # "progress":progress
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
        new_budget_progress.state = "draft"
        new_budget_progress.title = f"{budget_progress.title}"
        new_budget_progress.save()

        new_budget_progress.activity_domains.set(budget_progress.activity_domains.all())
        new_budget_progress.save()
        messages.success(request, f"{budget_progress.donor} financial report has been copied successfully.")
        # return HttpResponse(status=200)

    return redirect("create_project_budget_progress", project=project.pk)


@login_required
def update_budget_progress(request, project, pk):
    project_obj = get_object_or_404(Project, pk=project)
    budget_progress = get_object_or_404(BudgetProgress, pk=pk)

    form = BudgetProgressForm(instance=budget_progress, project=project_obj)
    if request.method == "POST":
        country = request.POST.get("country")
        form = BudgetProgressForm(request.POST, instance=budget_progress, project=project_obj)
        if form.is_valid():
            budget_progress = form.save(commit=False)
            activity_domain_ids = request.POST.getlist("activity_domains")
            budget_progress.project = project_obj
            budget_progress.country_id = country

            budget_progress.save()
            budget_progress.activity_domains.set(activity_domain_ids)
            activity_domain_names = f"{', '.join([str(ad) for ad in budget_progress.activity_domains.all()])}"
            budget_progress.title = f"{budget_progress.donor}: {activity_domain_names}"
            budget_progress.save()
            messages.success(request, "Financial report has been updated.")
            return redirect("create_project_budget_progress", project=project_obj.pk)

        else:
            messages.error(request, "Something went wrong. Please fix the below errors.")
    context = {"form": form}
    return render(request, "rh/financial_reports/project_budget_progress.html", context)


@login_required
def delete_budget_progress(request, pk):
    budget_progress = get_object_or_404(BudgetProgress, pk=pk)
    if budget_progress:
        budget_progress.delete()
        messages.success(request, f"{budget_progress.donor} financial report has been deleted.")
        return HttpResponse(status=200)
