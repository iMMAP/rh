from pymongo import MongoClient
from pprint import pprint
from bson.objectid import ObjectId
from datetime import datetime
import sqlite3
import pandas as pd

mongo_host = '127.0.0.1'

filter_date = datetime(2022, 1, 1)

def build_tmp(con, tbl, key_map, vals):
    str_cols = ','.join(['_id'] + [x for x in key_map.values()])
    str_sql_val = ','.join(['?'] * (len(key_map) + 1))

    entities = []
    for x in vals: 
        entity = []
        entity.append(str(x['_id']))
        for y in key_map.keys(): 
            val = x.get(y)
            if val == '':
                val = None
            # entity.append(x.get(y))
            entity.append(val)
        entities.append(entity)

    con.execute(f"CREATE TABLE {tbl} ({str_cols})")
    con.executemany(f'INSERT INTO {tbl} ({str_cols}) VALUES ({str_sql_val})', entities)
    con.commit()

def clean_org(value): 
    name = value.lower().strip()

    if name == 'save the children':
        value = 'Save The Children'

    if name == 'concern worldwide' or name == 'concern world wide':
        value = 'Concern WorldWide'

    if name == 'terre des hommes':
        value = 'Terre Des Hommes'

    if name == 'save the children federation international': 
        value = 'Save The Children'

    if name == 'zoa international':
        value = 'ZOA Refugee Care'

    return value.strip().title()

client = MongoClient(mongo_host)
db = client.ngmReportHub


con = sqlite3.connect("play.sqlite3")
# con = sqlite3.connect(":memory:")

users_list = list(db.user.find())

for user in users_list: 
    user['roles'] = ','.join(user['roles'])
    user['organization_name'] = clean_org(user['organization_name']) if 'organization_name' in user else None

key_map = {
    'organization_name': 'org_name',
    'organization': 'org_short',
    'cluster': 'cluster',
    'username': 'username',
    'password': 'password',
    'name': 'name',
    'position': 'position',
    'email': 'email',
    'admin0pcode': 'country',
    'phone': 'phone',
    'roles': 'roles',
    'programme_name': 'programme_name',
    'status': 'status',
    'visits': 'visits',
    'last_logged_in': 'last_logged_in',
    'createdAt': 'created_at',
    'updatedAt': 'updated_at'
}

build_tmp(con, 'tmp_user', key_map, users_list)

orgs_list = list(db.organizations.find())


df = pd.DataFrame(orgs_list)

df['organization_name'] = df['organization_name'].apply(clean_org)

unique_orgs = df[
    ['_id', 'organization_name', 'organization', 'organization_type', 'organization_tag']
].drop_duplicates(
    subset=['organization_name', 'organization', 'organization_type', 'organization_tag']).to_dict('records'
)

key_map = {
    'organization_name': 'name',
    'organization': 'short',
    'organization_tag': 'tag',
    'organization_type': 'type'
}


build_tmp(con, 'tmp_org', key_map, unique_orgs)

orgs_list = []

db = client.ngmHealthCluster

projects_list = list(db.project.find({
    'createdAt': { 
        '$gt': filter_date  
    },
}))

for project in projects_list:
    if project['project_description'] == 'Please complete an Activity Plan':
        project['project_description'] = ''
    project['organization_name'] = clean_org(project['organization_name'])

key_map = {
    'admin0pcode': 'country',
    'cluster': 'cluster',
    'email': 'email',
    'organization': 'org_short',
    'organization_name': 'org_name',
    'project_title': 'title',
    'project_description': 'description',
    'project_budget': 'budget',
    'project_start_date': 'start_date',
    'project_end_date': 'end_date',
    'createdAt': 'created_at',
    'updatedAt': 'updated_at'
}


build_tmp(con, 'tmp_project', key_map, projects_list)

projects_list = []



reports_list = list(db.report.find({
    'createdAt': { 
        '$gt': filter_date  
    },
    'report_year': { 
        '$gt': 2021
    },
}))

key_map = {
    'project_id': 'project__id',
    'report_active': 'active',
    'report_month': 'month',
    'report_year': 'year',
    'report_status': 'status',
    'report_submitted': 'submitted_at',
    'createdAt': 'created_at',
    'updatedAt': 'updated_at'
}

build_tmp(con, 'tmp_report', key_map, reports_list)

target_benefs = db.targetbeneficiaries.find({
    'createdAt': { 
        '$gt': datetime(2022, 1, 1)  
    },
})

key_map = {
    'project_id': 'project__id',
    'report_id': 'report__id',
    'activity_type_name': 'activity_type',
    'activity_description_name': 'activity_desc',
    'activity_detail_name': 'activity_detail',
    'beneficiary_category_name': 'benef_category',
    'indicator_name': 'indicator',
    'boys': 'boys',
    'girls': 'girls',
    'men': 'men',
    'women': 'women',
    'households': 'households',
    'elderly_men': 'elderly_men',
    'elderly_women': 'elderly_women',
    'total_pwd': 'total_pwd', 
    'createdAt': 'created_at',
    'updatedAt': 'updated_at'
}

build_tmp(con, 'tmp_target_benef', key_map, target_benefs)


benefs = db.beneficiaries.find({
    'createdAt': { 
        '$gt': datetime(2022, 1, 1)  
    },
    'report_year': { 
        '$gt': 2021
    },
})

benef_list = []
for ben in benefs: 
    if ben.get('response'):
        cnt = len(ben['response'])
        res = ''
        for i in range(0, cnt):
            if ben['response'][0] == '':
                continue
            res = res + ben['response'][i]['response_name'] + ','
        res = res.strip(',')

        ben['response'] = res
        # b['response'] = str(b['response'])
        benef_list.append(ben)

key_map = {
    'report_id': 'report__id',
    'activity_type_name': 'activity_type',
    'activity_description_name': 'activity_desc',
    'activity_detail_name': 'activity_detail',
    'beneficiary_category_name': 'benef_category',
    'beneficiary_type_name': 'benef_type',
    'hrp_beneficiary_type_name': 'hrp_benef_type',
    'transfer_category_name': 'transfer_category',
    'grant_type_name': 'grant_type',
    'delivery_type_name': 'delivery_type',
    'mpc_delivery_type_name': 'mpc_delivery_type',
    'mpc_mechanism_type_name': 'mpc_mechanism_type',
    'package_type_name': 'package_type',
    'unit_type_name': 'unit_type',
    'indicator_name': 'indicator',
    'response': 'response',
    'boys': 'boys',
    'girls': 'girls',
    'men': 'men',
    'women': 'women',
    'households': 'households',
    'elderly_men': 'elderly_men',
    'elderly_women': 'elderly_women',
    'total_pwd': 'total_pwd', 
    'admin0name': 'admin0name',
    'adminRpcode': 'adminRpcode',
    'admin1pcode': 'admin1pcode',
    'admin1name': 'admin1name',
    'admin2pcode': 'admin2pcode',
    'admin2name': 'admin2name',
    'site_type_name': 'site_type',
    'site_name': 'site_name',
    'createdAt': 'created_at',
    'updatedAt': 'updated_at',
}

build_tmp(con, 'tmp_benef', key_map, benef_list)





### BUILDING LOCATIONS ####
df = pd.read_csv('af_loc.csv')

df['Long'] = df['Long'].str.replace(',', '.').astype(float)
df['Lat'] = df['Lat'].str.replace(',', '.').astype(float)

df.to_sql('tmp_locs', con, index=False)

con.execute("""
CREATE TABLE locs (id INTEGER PRIMARY KEY AUTOINCREMENT, level, parent_id, code, name, original_name, type, lat, long);
""")

con.execute("""
insert into locs (level, parent_id, code, name, original_name, type)
select distinct 0 level, 0 parent, ADM0_PCODE code, ADM0_NA_EN name, ADM0_translation original_name, 'country' type from tmp_locs
""")

con.execute("""
insert into locs (level, parent_id, code, name, original_name, type)
select distinct 1 level, r.id as parent_id, ADM1_PCODE code, ADM1_NA_EN name, ADM1_translation original_name, 'province' type 
from tmp_locs t inner join locs r ON r.code = t.ADM0_PCODE;
""")

con.execute("""
insert into locs (level, parent_id, code, name, type, lat, long)
select distinct 2 level, r.id as parent_id, ADM2_PCODE code, ADM2_NA_EN name, 'district' type, t.lat, t.long 
from tmp_locs t inner join locs r ON r.code = t.ADM1_PCODE;
""")

con.commit()
###############################




sql_file = open("migrate.sql")
sql_as_string = sql_file.read()
con.executescript(sql_as_string)



for x in ['activity_type', 'activity_desc', 'activity_detail', 'indicator']:
    con.execute(f"""
    ALTER TABLE benef DROP COLUMN {x};
    """)
    con.execute(f"""
    ALTER TABLE target_benef DROP COLUMN {x};
    """)


for x in ['tmp_project', 'tmp_report', 'tmp_benef', 'tmp_locs', 'tmp_org', 'tmp_target_benef']:
    con.execute(f"""
    DROP TABLE {x};
    """)

con.commit()

con.execute("VACUUM")

