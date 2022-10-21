import random
import ast
import datetime

import django
django.setup()

from django.contrib.auth.models import User

from django.contrib.auth import get_user_model

import faker.providers
from django.core.management.base import BaseCommand

from faker import Faker
from ...models import *
from accounts.models import *
from stock.models import *

COUNTRIES = [ 
  {'name': 'Afghanistan', 'code': 'AF'}, 
  {'name': 'Somalia', 'code': 'SO'}, 
]

CLOCATION = {'parent': None, 'level': 0, 'name': 'Afghanistan', 'code': 'AF', 'original_name': 'افغانستان', 'type': 'Country', 'lat': 0, 'long': 0}
PLOCATION = [
    {'level': 1, 'name': 'Kabul', 'code': 'AF01', 'original_name': 'کابل', 'type': 'Province', 'lat': 0, 'long': 0},
    {'level': 1, 'name': 'Samangan', 'code': 'AF20', 'original_name': 'سمنگان', 'type': 'Province', 'lat': 0, 'long': 0},
    {'level': 1, 'name': 'Logar', 'code': 'AF05', 'original_name': 'لوگر', 'type': 'Province', 'lat': 0, 'long': 0},
    {'level': 1, 'name': 'Paktika', 'code': 'AF12', 'original_name': 'پکتیکا', 'type': 'Province', 'lat': 0, 'long': 0},
    {'level': 1, 'name': 'Sar-e-Pul', 'code': 'AF22', 'original_name': 'سرپل', 'type': 'Province', 'lat': 0, 'long': 0},
]
DLOCATION = [
    {'parent': 'AF01', 'level': 2, 'name': 'Estalef', 'code': 'AF0113', 'original_name': '', 'type': 'District', 'lat': 34.848476, 'long': 69.022911},
    {'parent': 'AF01', 'level': 2, 'name': 'Paghman', 'code': 'AF0102', 'original_name': '', 'type': 'District', 'lat': 34.541674, 'long': 68.935676},
    
    {'parent': 'AF20', 'level': 2, 'name': 'Feroz Nakhchir', 'code': 'AF2004', 'original_name': '', 'type': 'District', 'lat': 36.446451, 'long': 67.610323},
    {'parent': 'AF20', 'level': 2, 'name': 'Dara-e-Suf-e-Bala', 'code': 'AF2007', 'original_name': '', 'type': 'District', 'lat': 35.640448, 'long': 67/.262889},
    
    {'parent': 'AF05', 'level': 2, 'name': 'Khoshi', 'code': 'AF0504', 'original_name': '', 'type': 'District', 'lat': 33.992485, 'long': 69.284904},
    {'parent': 'AF05', 'level': 2, 'name': 'Mohammad Agha', 'code': 'AF0505', 'original_name': '', 'type': 'District', 'lat': 34.204792, 'long': 69.18032},

    {'parent': 'AF12', 'level': 2, 'name': 'Wormamay', 'code': 'AF1218', 'original_name': '', 'type': 'District', 'lat': 31.932197, 'long': 68.858521},
    {'parent': 'AF12', 'level': 2, 'name': 'Sharan', 'code': 'AF1201', 'original_name': '', 'type': 'District', 'lat': 33.211648, 'long': 68.74734},

    {'parent': 'AF22', 'level': 2, 'name': 'Balkhab', 'code': 'AF2207', 'original_name': '', 'type': 'District', 'lat': 35.453001, 'long': 35.928227},
    {'parent': 'AF22', 'level': 2, 'name': 'Gosfandi', 'code': 'AF2206', 'original_name': '', 'type': 'District', 'lat': 33.211648, 'long': 66.54342}
]

JSON3 = {
   "fields": [
      {
         "name":"Text Input",
         "type":"text"
      },      
      {
         "name":"Text Area",
         "type":"textarea"
      },
      {
         "name":"Integer Input",
         "type":"integer"
      },
      {
         "name":"Radio Select",
         "type":"radio",
         "value":[
            "Radio 1",
            "Radio 2",
            "Radio 3",
            "Radio 4"
         ]
      },
      {
         "name":"Simple Select",
         "type":"select",
         "value":[
            "Select 1",
            "Select 2",
            "Select 3",
            
         ]
      },
      {
         "name":"Check Box",
         "type":"checkbox"
      },
      {
         "name":"Multi Select Example",
         "type":"multi",
         "value":[
            "M Select 1",
            "M Select 2",
            "M Select 3",
            "M Select 4",
            "M Select 5",
            "M Select 6",
            "M Select 7"
         ]
      }
   ],
}

JSON2 = {
   "fields": [
      {
         "name":"Firstname",
         "type":"text"
      },
      {
         "name":"Lastname",
         "type":"text"
      },
      {
         "name":"Smallcv",
         "type":"textarea"
      },
      {
         "name":"Age",
         "type":"integer"
      },
      {
         "name":"Merital Status",
         "type":"radio",
         "value":[
            "Married",
            "Single",
            "Divorced",
            "Widower"
         ]
      },
      {
         "name":"Occupation",
         "type":"select",
         "value":[
            "Farmer",
            "Engineer",
            "Teacher",
            "Office Clerk",
            "Unemployed",
            "Retired",
            "Other"
         ]
      },
      {
         "name":"Internet",
         "type":"checkbox"
      },
      {
         "name":"Multi Select",
         "type":"multi",
         "value":[
            "Select 1",
            "Select 2",
            "Select 3",
            "Select 4"
         ]
      }
   ],
}

JSON1 = {
    "fields": [
        {
            "name": "Indicator",
            "type": "multi",
            "value": ["choice 1", "choice 2", "choice 3", "choice 4"]
        },
        {
            "name": "Winterization",
            "type": "checkbox"
        },
        {
            "name": "Covid",
            "type": "checkbox"
        },
        {
            "name": "Transfer Type",
            "type": "select",
            "value": ["cash", "hawala", "bank"]
        },
        {
            "name":"Population",
            "type":"integer"
        },
        {
            "name":"Availability Status",
            "type":"radio",
            "value":[
                "Busy",
                "Available",
                "Off",
                "Do not Disturb"
            ]
      },
    ]
}

class Provider(faker.providers.BaseProvider):
    def countries(self):
        return str(self.random_element(COUNTRIES))

    def unique_number(self, records_range):
        return random.randint(1, records_range)
    
    def unique_number_a(self, records_range):
        return random.randint(1, records_range)
    
    def unique_number_p(self, records_range):
        return random.randint(1, records_range)

    def unique_string(self, records_range, fake):
        return fake.text(max_nb_chars=5)
    
    def country_location(self):
        return str(CLOCATION)
    
    def province_location(self):
        return str(PLOCATION)
    
    def district_location(self):
        return str(DLOCATION)
    
    def stock_types_unique_number(self, records_range):
        return random.randint(1, records_range)

    def stock_units_unique_number(self, records_range):
        return random.randint(1, records_range)


class Command(BaseCommand):
    help = "Load Fictive Data"


    def handle(self, *args, **kwargs):

        fake = Faker()
        fake.add_provider(Provider)

        # Create Superuser
        user_model = get_user_model()
        username = 'admin'
        password = 'admin'
        email = f"{username}@{fake.domain_name()}"

        Admin = user_model.objects.filter(username="admin").first()
        try:
            if not Admin:
                Admin = user_model.objects.create_superuser(username, email, password)
        except Exception:
            self.stdout.write(self.style.Danger("Failed to create superuser"))

        self.stdout.write(self.style.SUCCESS(
            f"""
        Super User Created Successfully: 
        Username: {username}
        Password: {password}
        """))

        # Load Currency
        Currency.objects.all().delete()
        Currency.objects.bulk_create([
                        Currency(name='USD'),
                        Currency(name="EUR")
                        ]
                    )
            
        currency_count = Currency.objects.all().count()
        self.stdout.write(self.style.SUCCESS(f"Number of Currencies Created: {currency_count}"))


        # Load Countries
        Country.objects.all().delete()
        for _ in range(2):
            c = fake.unique.countries()
            c = ast.literal_eval(c)
            Country.objects.create(code=c['code'], name=c['name'])
        countries_count = Country.objects.all().count()
        self.stdout.write(self.style.SUCCESS(f"Number of Countries Created: {countries_count}"))

        
        # Load Clusters
        Cluster.objects.all().delete()
        for _ in range(3):
            c = fake.unique.unique_number(records_range=20)
            Cluster.objects.create(title=f"Cluster_{c}")
        clusters_count = Cluster.objects.all().count()
        self.stdout.write(self.style.SUCCESS(f"Number of Clusters Created: {clusters_count}"))


        # Load Locations
        Location.objects.all().delete()

        cl = fake.country_location()
        cl = ast.literal_eval(cl)
        clocation = Location.objects.create(parent=cl['parent'], level=cl['level'], 
                                name=cl['name'], code=cl['code'], 
                                original_name=cl['original_name'], 
                                type=cl['type'], lat=cl['lat'], long=cl['long']
                            )

        plocations = fake.province_location()
        plocations = ast.literal_eval(plocations)
        for pl in plocations:
            Location.objects.create(parent=clocation, level=pl['level'], 
                                    name=pl['name'], code=pl['code'], 
                                    original_name=pl['original_name'], 
                                    type=pl['type'], lat=pl['lat'], long=pl['long']
                                )

        dlocations = fake.district_location()
        dlocations = ast.literal_eval(dlocations)
        for dl in dlocations:
            parent_location = Location.objects.get(code=dl['parent'])
            Location.objects.create(parent=parent_location, level=dl['level'], 
                                    name=dl['name'], code=dl['code'], 
                                    original_name=dl['original_name'], 
                                    type=dl['type'], lat=dl['lat'], long=dl['long']
                                )
        
        locations_count = Location.objects.all().count()
        self.stdout.write(self.style.SUCCESS(f"Number of Locations Created: {locations_count}"))

        # Load Organizations
        Organization.objects.all().delete()
        for _ in range(3):
            o = fake.unique.unique_number(records_range=20)
            code = fake.unique.unique_string(records_range=20, fake=fake).upper().replace('.', '')
            type = fake.unique.text(max_nb_chars=20).replace('.', '')
            organization = Organization.objects.create(name=f"Organization_{o}", 
                                        code=code, type=type
                                    )
            for c in Country.objects.order_by('?')[0:fake.unique_number(records_range=3)]:
                organization.countires.add(c.id)
        organizations_count = Organization.objects.all().count()
        self.stdout.write(self.style.SUCCESS(f"Number of Organizations Created: {organizations_count}"))
        
        
        # Load Activities
        Activity.objects.all().delete()
        for j in range(3):
            a = fake.unique.unique_number_a(records_range=20)
            description = fake.unique.text(max_nb_chars=30).replace('.', '')
            activity = Activity.objects.create(
                                        title=f"Activity_{a}", 
                                        description=description,
                                        active=True,
                                        fields=JSON1 if j==1 else (JSON2 if j==2  else JSON3)
                                    )
            for c in Country.objects.order_by('?')[0:fake.unique_number(records_range=2)]:
                activity.countries.add(c.id)

            for cl in Cluster.objects.order_by('?')[0:fake.unique_number(records_range=2)]:
                activity.clusters.add(cl.id)
            
        activities_count = Activity.objects.all().count()
        self.stdout.write(self.style.SUCCESS(f"Number of Activities Created: {activities_count}"))


        # Load Projects
        Project.objects.all().delete()
        for _ in range(3):
            p = fake.unique.unique_number_p(records_range=20)
            description = fake.text(max_nb_chars=30).replace('.', '')
            project = Project.objects.create(
                                user=Admin,
                                title=f"Project_{p}", 
                                description=description,
                                start_date=datetime.datetime.today().date(),
                                end_date=datetime.datetime.now().date() + datetime.timedelta(days=random.randint(10, 40)),
                                budget=random.randint(1, 50)*1000,
                                budget_currency=Currency.objects.order_by('?')[0],
                            )
            for a in Activity.objects.order_by('?')[0:fake.unique_number(records_range=2)]:
                project.activities.add(a.id)

            for cl in Cluster.objects.order_by('?')[0:fake.unique_number(records_range=2)]:
                project.clusters.add(cl.id)
            
            for loc in Location.objects.order_by('?')[0:fake.unique_number(records_range=2)]:
                project.locations.add(loc.id)
            
        projects_count = Project.objects.all().count()
        self.stdout.write(self.style.SUCCESS(f"Number of Projects Created: {projects_count}"))

        # Load Activity Plans
        ActivityPlan.objects.all().delete()
        for _ in range(3):
            ActivityPlan.objects.create(
                            project=Project.objects.order_by('?')[0],
                            activity=Activity.objects.order_by('?')[0],
                            boys=random.randint(1, 500),
                            girls=random.randint(1, 500),
                            men=random.randint(1, 500),
                            women=random.randint(1, 500),
                            elderly_men=random.randint(1, 500),
                            elderly_women=random.randint(1, 500),
                            households=random.randint(1, 500),
                        )
            
        activity_plans_count = ActivityPlan.objects.all().count()
        self.stdout.write(self.style.SUCCESS(f"Number of Activity Plans Created: {activity_plans_count}"))

        
        # Load Clusters
        StockType.objects.all().delete()
        for _ in range(4):
            c = fake.unique.stock_types_unique_number(records_range=20)
            StockType.objects.create(name=f"Stock Type {c}")
        stock_types_count = StockType.objects.all().count()
        self.stdout.write(self.style.SUCCESS(f"Number of Stock Types Created: {stock_types_count}"))


        # Load Clusters
        StockUnit.objects.all().delete()
        for _ in range(4):
            c = fake.unique.stock_units_unique_number(records_range=20)
            StockUnit.objects.create(name=f"Stock Unit {c}")
        stock_units_count = StockUnit.objects.all().count()
        self.stdout.write(self.style.SUCCESS(f"Number of Stock Units Created: {stock_units_count}"))