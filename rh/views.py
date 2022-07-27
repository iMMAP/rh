from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import loader

def index(request):
    template = loader.get_template('index.html')
    context = {'hey': 'alaki'}
    return HttpResponse(template.render(context, request))


def profile(request):
    template = loader.get_template('rh/profile.html')
    user = request.user
    context = {'user': user}
    return HttpResponse(template.render(context, request))


# def add_project(request):
#     if request.method == 'POST':
#         project = Project(
#             user=request.user,
#             title=request.POST['title'],
#             description=request.POST['description'],
#             start_date=request.POST['start_date'],
#             end_date=request.POST['end_date'],
#         )

#         project.save()
#         #return HttpResponseRedirect(reverse('index', args=(project.id,)))
#         return HttpResponseRedirect('/profile/')
    
#     else:
#         form = ProjectForm()
#         return render(request, 'report/add.html', {'form': form})
#         # template = loader.get_template('report/add.html')
#         # user = request.user
#         # context = {'user': user}
#         # return HttpResponse(template.render(context, request))
