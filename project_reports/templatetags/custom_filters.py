from django import template

register = template.Library()

@register.filter
def custom_class(report):
    if report.state == 'pending':
        return 'olive'
    elif (report.state == 'todo' and report.report_date < report.report_due_date) or report.state == 'complete':
        return 'green'
    elif report.state != 'complete' and report.report_date > report.report_due_date:
        return 'red'
    else:
        return ''
