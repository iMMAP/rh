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

COUNTRIES = [ 
  {'name': 'Afghanistan', 'code': 'AF'}, 
  {'name': 'Åland Islands', 'code': 'AX'}, 
  {'name': 'Albania', 'code': 'AL'}, 
  {'name': 'Algeria', 'code': 'DZ'}, 
  {'name': 'American Samoa', 'code': 'AS'}, 
  {'name': 'AndorrA', 'code': 'AD'}, 
  {'name': 'Angola', 'code': 'AO'}, 
  {'name': 'Anguilla', 'code': 'AI'}, 
  {'name': 'Antarctica', 'code': 'AQ'}, 
  {'name': 'Antigua and Barbuda', 'code': 'AG'}, 
  {'name': 'Argentina', 'code': 'AR'}, 
  {'name': 'Armenia', 'code': 'AM'}, 
  {'name': 'Aruba', 'code': 'AW'}, 
  {'name': 'Australia', 'code': 'AU'}, 
  {'name': 'Austria', 'code': 'AT'}, 
  {'name': 'Azerbaijan', 'code': 'AZ'}, 
  {'name': 'Bahamas', 'code': 'BS'}, 
  {'name': 'Bahrain', 'code': 'BH'}, 
  {'name': 'Bangladesh', 'code': 'BD'}, 
  {'name': 'Barbados', 'code': 'BB'}, 
  {'name': 'Belarus', 'code': 'BY'}, 
  {'name': 'Belgium', 'code': 'BE'}, 
  {'name': 'Belize', 'code': 'BZ'}, 
  {'name': 'Benin', 'code': 'BJ'}, 
  {'name': 'Bermuda', 'code': 'BM'}, 
  {'name': 'Bhutan', 'code': 'BT'}, 
  {'name': 'Bolivia', 'code': 'BO'}, 
  {'name': 'Bosnia and Herzegovina', 'code': 'BA'}, 
  {'name': 'Botswana', 'code': 'BW'}, 
  {'name': 'Bouvet Island', 'code': 'BV'}, 
  {'name': 'Brazil', 'code': 'BR'}, 
  {'name': 'British Indian Ocean Territory', 'code': 'IO'}, 
  {'name': 'Brunei Darussalam', 'code': 'BN'}, 
  {'name': 'Bulgaria', 'code': 'BG'}, 
  {'name': 'Burkina Faso', 'code': 'BF'}, 
  {'name': 'Burundi', 'code': 'BI'}, 
  {'name': 'Cambodia', 'code': 'KH'}, 
  {'name': 'Cameroon', 'code': 'CM'}, 
  {'name': 'Canada', 'code': 'CA'}, 
  {'name': 'Cape Verde', 'code': 'CV'}, 
  {'name': 'Cayman Islands', 'code': 'KY'}, 
  {'name': 'Central African Republic', 'code': 'CF'}, 
  {'name': 'Chad', 'code': 'TD'}, 
  {'name': 'Chile', 'code': 'CL'}, 
  {'name': 'China', 'code': 'CN'}, 
  {'name': 'Christmas Island', 'code': 'CX'}, 
  {'name': 'Cocos (Keeling) Islands', 'code': 'CC'}, 
  {'name': 'Colombia', 'code': 'CO'}, 
  {'name': 'Comoros', 'code': 'KM'}, 
  {'name': 'Congo', 'code': 'CG'}, 
  {'name': 'Congo, The Democratic Republic of the', 'code': 'CD'}, 
  {'name': 'Cook Islands', 'code': 'CK'}, 
  {'name': 'Costa Rica', 'code': 'CR'}, 
  {'name': 'Cote D\'Ivoire', 'code': 'CI'}, 
  {'name': 'Croatia', 'code': 'HR'}, 
  {'name': 'Cuba', 'code': 'CU'}, 
  {'name': 'Cyprus', 'code': 'CY'}, 
  {'name': 'Czech Republic', 'code': 'CZ'}, 
  {'name': 'Denmark', 'code': 'DK'}, 
  {'name': 'Djibouti', 'code': 'DJ'}, 
  {'name': 'Dominica', 'code': 'DM'}, 
  {'name': 'Dominican Republic', 'code': 'DO'}, 
  {'name': 'Ecuador', 'code': 'EC'}, 
  {'name': 'Egypt', 'code': 'EG'}, 
  {'name': 'El Salvador', 'code': 'SV'}, 
  {'name': 'Equatorial Guinea', 'code': 'GQ'}, 
  {'name': 'Eritrea', 'code': 'ER'}, 
  {'name': 'Estonia', 'code': 'EE'}, 
  {'name': 'Ethiopia', 'code': 'ET'}, 
  {'name': 'Falkland Islands (Malvinas)', 'code': 'FK'}, 
  {'name': 'Faroe Islands', 'code': 'FO'}, 
  {'name': 'Fiji', 'code': 'FJ'}, 
  {'name': 'Finland', 'code': 'FI'}, 
  {'name': 'France', 'code': 'FR'}, 
  {'name': 'French Guiana', 'code': 'GF'}, 
  {'name': 'French Polynesia', 'code': 'PF'}, 
  {'name': 'French Southern Territories', 'code': 'TF'}, 
  {'name': 'Gabon', 'code': 'GA'}, 
  {'name': 'Gambia', 'code': 'GM'}, 
  {'name': 'Georgia', 'code': 'GE'}, 
  {'name': 'Germany', 'code': 'DE'}, 
  {'name': 'Ghana', 'code': 'GH'}, 
  {'name': 'Gibraltar', 'code': 'GI'}, 
  {'name': 'Greece', 'code': 'GR'}, 
  {'name': 'Greenland', 'code': 'GL'}, 
  {'name': 'Grenada', 'code': 'GD'}, 
  {'name': 'Guadeloupe', 'code': 'GP'}, 
  {'name': 'Guam', 'code': 'GU'}, 
  {'name': 'Guatemala', 'code': 'GT'}, 
  {'name': 'Guernsey', 'code': 'GG'}, 
  {'name': 'Guinea', 'code': 'GN'}, 
  {'name': 'Guinea-Bissau', 'code': 'GW'}, 
  {'name': 'Guyana', 'code': 'GY'}, 
  {'name': 'Haiti', 'code': 'HT'}, 
  {'name': 'Heard Island and Mcdonald Islands', 'code': 'HM'}, 
  {'name': 'Holy See (Vatican City State)', 'code': 'VA'}, 
  {'name': 'Honduras', 'code': 'HN'}, 
  {'name': 'Hong Kong', 'code': 'HK'}, 
  {'name': 'Hungary', 'code': 'HU'}, 
  {'name': 'Iceland', 'code': 'IS'}, 
  {'name': 'India', 'code': 'IN'}, 
  {'name': 'Indonesia', 'code': 'ID'}, 
  {'name': 'Iran, Islamic Republic Of', 'code': 'IR'}, 
  {'name': 'Iraq', 'code': 'IQ'}, 
  {'name': 'Ireland', 'code': 'IE'}, 
  {'name': 'Isle of Man', 'code': 'IM'}, 
  {'name': 'Israel', 'code': 'IL'}, 
  {'name': 'Italy', 'code': 'IT'}, 
  {'name': 'Jamaica', 'code': 'JM'}, 
  {'name': 'Japan', 'code': 'JP'}, 
  {'name': 'Jersey', 'code': 'JE'}, 
  {'name': 'Jordan', 'code': 'JO'}, 
  {'name': 'Kazakhstan', 'code': 'KZ'}, 
  {'name': 'Kenya', 'code': 'KE'}, 
  {'name': 'Kiribati', 'code': 'KI'}, 
  {'name': 'Korea, Democratic People\'S Republic of', 'code': 'KP'}, 
  {'name': 'Korea, Republic of', 'code': 'KR'}, 
  {'name': 'Kuwait', 'code': 'KW'}, 
  {'name': 'Kyrgyzstan', 'code': 'KG'}, 
  {'name': 'Lao People\'S Democratic Republic', 'code': 'LA'}, 
  {'name': 'Latvia', 'code': 'LV'}, 
  {'name': 'Lebanon', 'code': 'LB'}, 
  {'name': 'Lesotho', 'code': 'LS'}, 
  {'name': 'Liberia', 'code': 'LR'}, 
  {'name': 'Libyan Arab Jamahiriya', 'code': 'LY'}, 
  {'name': 'Liechtenstein', 'code': 'LI'}, 
  {'name': 'Lithuania', 'code': 'LT'}, 
  {'name': 'Luxembourg', 'code': 'LU'}, 
  {'name': 'Macao', 'code': 'MO'}, 
  {'name': 'Macedonia, The Former Yugoslav Republic of', 'code': 'MK'}, 
  {'name': 'Madagascar', 'code': 'MG'}, 
  {'name': 'Malawi', 'code': 'MW'}, 
  {'name': 'Malaysia', 'code': 'MY'}, 
  {'name': 'Maldives', 'code': 'MV'}, 
  {'name': 'Mali', 'code': 'ML'}, 
  {'name': 'Malta', 'code': 'MT'}, 
  {'name': 'Marshall Islands', 'code': 'MH'}, 
  {'name': 'Martinique', 'code': 'MQ'}, 
  {'name': 'Mauritania', 'code': 'MR'}, 
  {'name': 'Mauritius', 'code': 'MU'}, 
  {'name': 'Mayotte', 'code': 'YT'}, 
  {'name': 'Mexico', 'code': 'MX'}, 
  {'name': 'Micronesia, Federated States of', 'code': 'FM'}, 
  {'name': 'Moldova, Republic of', 'code': 'MD'}, 
  {'name': 'Monaco', 'code': 'MC'}, 
  {'name': 'Mongolia', 'code': 'MN'}, 
  {'name': 'Montserrat', 'code': 'MS'}, 
  {'name': 'Morocco', 'code': 'MA'}, 
  {'name': 'Mozambique', 'code': 'MZ'}, 
  {'name': 'Myanmar', 'code': 'MM'}, 
  {'name': 'Namibia', 'code': 'NA'}, 
  {'name': 'Nauru', 'code': 'NR'}, 
  {'name': 'Nepal', 'code': 'NP'}, 
  {'name': 'Netherlands', 'code': 'NL'}, 
  {'name': 'Netherlands Antilles', 'code': 'AN'}, 
  {'name': 'New Caledonia', 'code': 'NC'}, 
  {'name': 'New Zealand', 'code': 'NZ'}, 
  {'name': 'Nicaragua', 'code': 'NI'}, 
  {'name': 'Niger', 'code': 'NE'}, 
  {'name': 'Nigeria', 'code': 'NG'}, 
  {'name': 'Niue', 'code': 'NU'}, 
  {'name': 'Norfolk Island', 'code': 'NF'}, 
  {'name': 'Northern Mariana Islands', 'code': 'MP'}, 
  {'name': 'Norway', 'code': 'NO'}, 
  {'name': 'Oman', 'code': 'OM'}, 
  {'name': 'Pakistan', 'code': 'PK'}, 
  {'name': 'Palau', 'code': 'PW'}, 
  {'name': 'Palestinian Territory, Occupied', 'code': 'PS'}, 
  {'name': 'Panama', 'code': 'PA'}, 
  {'name': 'Papua New Guinea', 'code': 'PG'}, 
  {'name': 'Paraguay', 'code': 'PY'}, 
  {'name': 'Peru', 'code': 'PE'}, 
  {'name': 'Philippines', 'code': 'PH'}, 
  {'name': 'Pitcairn', 'code': 'PN'}, 
  {'name': 'Poland', 'code': 'PL'}, 
  {'name': 'Portugal', 'code': 'PT'}, 
  {'name': 'Puerto Rico', 'code': 'PR'}, 
  {'name': 'Qatar', 'code': 'QA'}, 
  {'name': 'Reunion', 'code': 'RE'}, 
  {'name': 'Romania', 'code': 'RO'}, 
  {'name': 'Russian Federation', 'code': 'RU'}, 
  {'name': 'RWANDA', 'code': 'RW'}, 
  {'name': 'Saint Helena', 'code': 'SH'}, 
  {'name': 'Saint Kitts and Nevis', 'code': 'KN'}, 
  {'name': 'Saint Lucia', 'code': 'LC'}, 
  {'name': 'Saint Pierre and Miquelon', 'code': 'PM'}, 
  {'name': 'Saint Vincent and the Grenadines', 'code': 'VC'}, 
  {'name': 'Samoa', 'code': 'WS'}, 
  {'name': 'San Marino', 'code': 'SM'}, 
  {'name': 'Sao Tome and Principe', 'code': 'ST'}, 
  {'name': 'Saudi Arabia', 'code': 'SA'}, 
  {'name': 'Senegal', 'code': 'SN'}, 
  {'name': 'Serbia and Montenegro', 'code': 'CS'}, 
  {'name': 'Seychelles', 'code': 'SC'}, 
  {'name': 'Sierra Leone', 'code': 'SL'}, 
  {'name': 'Singapore', 'code': 'SG'}, 
  {'name': 'Slovakia', 'code': 'SK'}, 
  {'name': 'Slovenia', 'code': 'SI'}, 
  {'name': 'Solomon Islands', 'code': 'SB'}, 
  {'name': 'Somalia', 'code': 'SO'}, 
  {'name': 'South Africa', 'code': 'ZA'}, 
  {'name': 'South Georgia and the South Sandwich Islands', 'code': 'GS'}, 
  {'name': 'Spain', 'code': 'ES'}, 
  {'name': 'Sri Lanka', 'code': 'LK'}, 
  {'name': 'Sudan', 'code': 'SD'}, 
  {'name': 'Suriname', 'code': 'SR'}, 
  {'name': 'Svalbard and Jan Mayen', 'code': 'SJ'}, 
  {'name': 'Swaziland', 'code': 'SZ'}, 
  {'name': 'Sweden', 'code': 'SE'}, 
  {'name': 'Switzerland', 'code': 'CH'}, 
  {'name': 'Syrian Arab Republic', 'code': 'SY'}, 
  {'name': 'Taiwan, Province of China', 'code': 'TW'}, 
  {'name': 'Tajikistan', 'code': 'TJ'}, 
  {'name': 'Tanzania, United Republic of', 'code': 'TZ'}, 
  {'name': 'Thailand', 'code': 'TH'}, 
  {'name': 'Timor-Leste', 'code': 'TL'}, 
  {'name': 'Togo', 'code': 'TG'}, 
  {'name': 'Tokelau', 'code': 'TK'}, 
  {'name': 'Tonga', 'code': 'TO'}, 
  {'name': 'Trinidad and Tobago', 'code': 'TT'}, 
  {'name': 'Tunisia', 'code': 'TN'}, 
  {'name': 'Turkey', 'code': 'TR'}, 
  {'name': 'Turkmenistan', 'code': 'TM'}, 
  {'name': 'Turks and Caicos Islands', 'code': 'TC'}, 
  {'name': 'Tuvalu', 'code': 'TV'}, 
  {'name': 'Uganda', 'code': 'UG'}, 
  {'name': 'Ukraine', 'code': 'UA'}, 
  {'name': 'United Arab Emirates', 'code': 'AE'}, 
  {'name': 'United Kingdom', 'code': 'GB'}, 
  {'name': 'United States', 'code': 'US'}, 
  {'name': 'United States Minor Outlying Islands', 'code': 'UM'}, 
  {'name': 'Uruguay', 'code': 'UY'}, 
  {'name': 'Uzbekistan', 'code': 'UZ'}, 
  {'name': 'Vanuatu', 'code': 'VU'}, 
  {'name': 'Venezuela', 'code': 'VE'}, 
  {'name': 'Viet Nam', 'code': 'VN'}, 
  {'name': 'Virgin Islands, British', 'code': 'VG'}, 
  {'name': 'Virgin Islands, U.S.', 'code': 'VI'}, 
  {'name': 'Wallis and Futuna', 'code': 'WF'}, 
  {'name': 'Western Sahara', 'code': 'EH'}, 
  {'name': 'Yemen', 'code': 'YE'}, 
  {'name': 'Zambia', 'code': 'ZM'}, 
  {'name': 'Zimbabwe', 'code': 'ZW'} 
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

JSON_VALUES = {
   "fields":[
      {
         "name":"firstname",
         "type":"text"
      },
      {
         "name":"lastname",
         "type":"text"
      },
      {
         "name":"smallcv",
         "type":"textarea"
      },
      {
         "name":"age",
         "type":"integer"
      },
      {
         "name":"marital_status",
         "type":"radio",
         "value":[
            "Married",
            "Single",
            "Divorced",
            "Widower"
         ]
      },
      {
         "name":"occupation",
         "label":"Occupation",
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
         "name":"internet",
         "type":"checkbox"
      },
      {
         "name":"indicator",
         "type":"multi",
         "value":[
            "choice 1",
            "choice 2",
            "choice 3",
            "choice 4"
         ]
      }
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


class Command(BaseCommand):
    help = "Load Fictive Data"


    def handle(self, *args, **kwargs):

        fake = Faker()
        fake.add_provider(Provider)

        # Create Superuser
        user_model = get_user_model()
        Admin = user_model.objects.filter(username="admin").first()
        try:
            if not Admin:
                Admin = user_model.objects.create_superuser('admin', 'admin@admin.cokm', 'admin')
        except Exception:
            self.stdout.write(self.style.Danger("Failed to create superuser"))


        # Load Currency
        Currency.objects.all().delete()
        Currency.objects.bulk_create([
                        Currency(code="USD", 
                        name='United States Dollar',
                        symbol='$'),
                        Currency(code="EUR", 
                        name='Euro',
                        symbol='€')
                        ]
                    )
            
        currency_count = Currency.objects.all().count()
        self.stdout.write(self.style.SUCCESS(f"Number of Currencies Created: {currency_count}"))


        # Load Countries
        Country.objects.all().delete()
        for _ in range(10):
            c = fake.unique.countries()
            c = ast.literal_eval(c)
            Country.objects.create(code=c['code'], name=c['name'])
        countries_count = Country.objects.all().count()
        self.stdout.write(self.style.SUCCESS(f"Number of Countries Created: {countries_count}"))

        
        # Load Clusters
        Cluster.objects.all().delete()
        for _ in range(10):
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
        for _ in range(10):
            o = fake.unique.unique_number(records_range=20)
            code = fake.unique.unique_string(records_range=20, fake=fake).upper().replace('.', '')
            type = fake.unique.text(max_nb_chars=20).replace('.', '')
            organization = Organization.objects.create(name=f"Organization_{o}", 
                                        code=code, type=type
                                    )
            for c in Country.objects.order_by('?')[0:fake.unique_number(records_range=4)]:
                organization.countires.add(c.id)
        organizations_count = Organization.objects.all().count()
        self.stdout.write(self.style.SUCCESS(f"Number of Organizations Created: {organizations_count}"))
        
        
        # Load Activities
        Activity.objects.all().delete()
        for _ in range(10):
            a = fake.unique.unique_number_a(records_range=20)
            description = fake.unique.text(max_nb_chars=30).replace('.', '')
            activity = Activity.objects.create(
                                        title=f"Activity_{a}", 
                                        description=description,
                                        active=True,
                                        fields=JSON_VALUES
                                    )
            for c in Country.objects.order_by('?')[0:fake.unique_number(records_range=4)]:
                activity.countries.add(c.id)

            for cl in Cluster.objects.order_by('?')[0:fake.unique_number(records_range=4)]:
                activity.clusters.add(cl.id)
            
        activities_count = Activity.objects.all().count()
        self.stdout.write(self.style.SUCCESS(f"Number of Activities Created: {activities_count}"))


        # Load Projects
        Project.objects.all().delete()
        for _ in range(10):
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
            for a in Activity.objects.order_by('?')[0:fake.unique_number(records_range=4)]:
                project.activities.add(a.id)

            for cl in Cluster.objects.order_by('?')[0:fake.unique_number(records_range=4)]:
                project.clusters.add(cl.id)
            
            for loc in Location.objects.order_by('?')[0:fake.unique_number(records_range=4)]:
                project.locations.add(loc.id)
            
        projects_count = Project.objects.all().count()
        self.stdout.write(self.style.SUCCESS(f"Number of Projects Created: {projects_count}"))

        # Load Activity Plans
        ActivityPlan.objects.all().delete()
        for _ in range(10):
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
