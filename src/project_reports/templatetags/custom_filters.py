from django import template

register = template.Library()


@register.filter
def custom_class(report):
    state = ""
    if report.state == "pending":
        state = "olive"
    if report.report_date and report.report_due_date:
        if (report.state == "todo" and report.report_date < report.report_due_date) or report.state == "complete":
            state = "green"
        elif report.state != "complete" and report.report_date > report.report_due_date:
            state = "red"
        elif report.state != "archive" and report.report_date > report.report_due_date:
            state = "red"
    return state
