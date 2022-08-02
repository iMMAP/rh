from email import message
from django.shortcuts import render
from django.contrib import messages

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .models import Project
from .forms import ProjectForm

def index(request):
    template = loader.get_template('index.html')
    context = {'hey': 'alaki'}
    return HttpResponse(template.render(context, request))


def profile(request):
    template = loader.get_template('profile.html')
    user = request.user
    context = {'user': user}
    return HttpResponse(template.render(context, request))


def add_project(request):
    if "Can view organization":
        if request.method == 'POST':
            form = ProjectForm(request.POST)
            project = Project(
            user=request.user,
            title=request.POST['title'],
            description=request.POST['description'],
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            )

            if form.is_valid():
                project.save()
                #return HttpResponseRedirect(reverse('index', args=(project.id,)))
                # messages.info(request, "Report saved successfully")
                return HttpResponseRedirect('/profile/')
            
        else:
            form = ProjectForm()
        return render(request, 'add_report.html', {'form': form})
            # template = loader.get_template('report/add.html')
            # user = request.user
            # context = {'user': user}
            # return HttpResponse(template.render(context, request))
