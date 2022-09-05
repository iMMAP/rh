from email import message
from django.shortcuts import render
from django.contrib import messages

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.conf import settings
from .models import Project
from .forms import ProjectForm
import datetime

import pandas as pd
import sqlite3

def index(request):
    template = loader.get_template('index.html')

    play_db = settings.PLAY_DB
    con = sqlite3.connect(play_db)

    play = con.execute("""
SELECT 
DATE('2022-0' || (r.month +1) || '-01') as month,
SUM(boys) + SUM(girls) + SUM(men) + SUM(women) + SUM(elderly_women) + SUM(elderly_men) AS people_recieved
FROM benef b 
INNER JOIN report r on b.report_id=r.id
INNER JOIN activity a on a.id = b.activity_id
INNER JOIN project p on p.id=r.project_id
INNER JOIN org o on o.id=p.org_id
INNER JOIN locs on locs.id = b.loc_id
WHERE substr(locs.code, 0, 3) = 'AF' AND 
o.short <> 'iMMAP' AND 
r.year = 2022
GROUP BY r.month
ORDER BY month
""")

    types = []
    nb_benef = []
    for x in play:
        types.append(
            datetime.date.fromisoformat(x[0]).strftime('%B')
        )
        nb_benef.append(x[1])

    
    months = str(types[0:10])
    benefs = str(nb_benef[0:10])

    df = pd.read_sql("""
SELECT 
DATE('2022-0' || (r.month +1) || '-01') as month, p.cluster,
--a.activity_type || ' - ' || a.activity_desc as activity,
SUM(boys) + SUM(girls) + SUM(men) + SUM(women) + SUM(elderly_women) + SUM(elderly_men) AS people_recieved
FROM benef b 
INNER JOIN report r on b.report_id=r.id
INNER JOIN activity a on a.id = b.activity_id
INNER JOIN project p on p.id=r.project_id
INNER JOIN org o on o.id=p.org_id
INNER JOIN locs on locs.id = b.loc_id
WHERE substr(locs.code, 0, 3) = 'AF' AND 
o.short <> 'iMMAP' AND 
r.year = 2022 AND
p.cluster IN ('ESNFI', 'FSAC', 'Protection', 'WASH')
GROUP BY r.month, p.cluster
ORDER BY month, cluster;
    """, con=con)
    
    clusters = df.pivot(index='month', columns='cluster', values='people_recieved').convert_dtypes().fillna(0).to_dict('list')

    df = pd.read_sql("""
    SELECT 
a.activity_type || ' - ' || a.activity_desc as activity, o.short, l2.name,
printf("%,d", SUM(boys) + SUM(girls) + SUM(men) + SUM(women) + SUM(elderly_women) + SUM(elderly_men)) AS people_recieved
FROM benef b 
INNER JOIN report r on b.report_id=r.id
INNER JOIN activity a on a.id = b.activity_id
INNER JOIN project p on p.id=r.project_id
INNER JOIN org o on o.id=p.org_id
INNER JOIN locs on locs.id = b.loc_id
INNER JOIN locs l2 on locs.parent_id = l2.id
WHERE substr(locs.code, 0, 3) = 'AF' AND 
o.short <> 'iMMAP' AND 
r.year = 2022 AND
r.month = 6 AND r.status='complete'
GROUP BY l2.id, activity_type, activity_desc HAVING people_recieved IS NOT NULL
ORDER BY month, l2.name, people_recieved desc;
    """, con=con)

    activities = df.to_dict('records')
    # import pdb; pdb.set_trace()
    context = {
        'months': months, 
        'benefs': benefs,
        'ESNFI': clusters['ESNFI'],
        'FSAC': clusters['FSAC'],
        'Protection': clusters['Protection'],
        'WASH': clusters['WASH'],
        'activities': activities,
    }

    return HttpResponse(template.render(context, request))


def profile(request):
    template = loader.get_template('profile.html')
    user = request.user
    context = {'user': user}
    return HttpResponse(template.render(context, request))


def add_project(request):
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
