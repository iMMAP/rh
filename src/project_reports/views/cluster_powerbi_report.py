from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from ..models import (
    ClusterDashboardReport,
)

@require_POST
@login_required
def fetch_cluster_report(request):
    cluster_code = request.POST.get('cluster_code')
    powerbi_report_url = None
    message = None

    if cluster_code:
        cluster = request.user.profile.clusters.filter(code=cluster_code).first()
        if cluster:
            report = ClusterDashboardReport.objects.filter(cluster=cluster).first()
            powerbi_report_url = report.report_link if report else None
        if not powerbi_report_url:
            message = "No report available for the selected cluster..."
    else:
        message = "Invalid cluster selected..."

    response_data = {
        'powerbi_report_url': powerbi_report_url,
        'message': message
    }

    return JsonResponse(response_data)
