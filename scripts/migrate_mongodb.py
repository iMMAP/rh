import sqlite3
import traceback
from datetime import datetime

import pandas as pd
import sqlalchemy
from pymongo import MongoClient

# from myapp.models import MyModel

# class Command(BaseCommand):
#     def handle(self, *args, **options):
#         # Read CSV file
#         data = pd.read_csv('data.csv')

#         # Convert CSV data to JSON
#         json_data = json.loads(data.to_json(orient='records'))

#         # Iterate over JSON data and create MyModel objects
#         for item in json_data:
#             mymodel = MyModel(json_field=item)
#             mymodel.save()


TEST = False  # set to False if working with test database and provide sqlite3 database

# SET THE FILE PATHS
SQLITEDB_PATH = '../db.sqlite3'

# CSV DATA FILES
CURRENCIES_CSV = '../data/currencies.csv'
LOCATIONS_CSV = '../data/af_loc.csv'
CLUSTERS_CSV = '../data/updated_clusters.csv'
ORGANIZATIONS_CSV = '../data/organizations.csv'
BENEFICIARY_TYPES_CSV = '../data/beneficiarytypes.csv'
DONORS_CSV = '../data/donors.csv'
INDICATORS_CSV = '../data/Indicators.csv'
ACTIVITIES_CSV = '../data/activities.csv'
USERS_CSV = '../data/user.csv'


class DataImporter():
    mongo_host = '127.0.0.1'
    filter_date = datetime(2022, 1, 1)
    test = True

    def __init__(self, test):
        """
        Set the test variable
        """
        self.test = test

    def build_tmp(self, con, tbl, key_map, vals):
        """
        Build a table and insert data
        """
        str_cols = ','.join(['_id'] + [x for x in key_map.values()] if self.test else [x for x in key_map.values()])
        str_sql_val = ','.join(['?'] * (len(key_map) + 1 if self.test else len(key_map)))

        entities = []
        for x in vals:
            if tbl in ['rh_cluster', 'tmp_cluster']:
                if x.get('cluster_id') in [e[1] for e in entities]:
                    continue
            if tbl in ['rh_organization', "tmp_organization"]:
                if x.get('organization_name') in [e[1] for e in entities]:
                    continue
            entity = []
            entity.append(str(x['_id']))
            for y in key_map.keys():
                val = x.get(y)
                if val == '':
                    val = None
                # entity.append(x.get(y))
                entity.append(val)
            entities.append(entity)

        cursor = con.cursor()
        if self.test:
            cursor.execute(f"CREATE TABLE {tbl} ({str_cols})")

        rows = []
        for entity in entities:
            if not self.test:
                _id = entity.pop(0)
                # str_cols = str_cols.replace('_id,', '')
            query = f"INSERT INTO {tbl}({str_cols}) VALUES ({str_sql_val})"
            try:
                cursor.execute(query, entity)
            except Exception as e:
                print(e)

            if not self.test:
                entity.insert(0, _id)
            rows.append({cursor.lastrowid: entity})

        return rows

    def get_mongo_client(self):
        """
        Returns a MongoClient instance.
        """
        return MongoClient(self.mongo_host)

    def get_sqlite_client(self, dbname):
        """
        Returns a SqliteClient instance.
        """
        return sqlite3.connect(dbname)

    def get_postgres_client(self, dbname):

        engine = sqlalchemy.create_engine('postgresql://postgres:f4d11447@localhost/rhtest')

        # engine = sqlalchemy.create_engine('impala://', creator=conn)
        return engine

    def import_currencies_from_csv(self, connection, currencies_csv):
        """
        Import Currencies from CSV
        """
        c = connection.cursor()
        df = pd.DataFrame()
        df = pd.read_csv(currencies_csv)

        if len(df) > 0:
            table = "rh_currency"

            df.to_sql('tmp_currency', connection, if_exists='replace', index=False)

            try:
                c.execute(f"""insert into {table}(name) select name from tmp_currency""")
                c.execute("DROP TABLE tmp_currency;")
            except Exception as e:
                connection.rollback()

    def import_locations(self, connection, locations_csv):
        """
        Import locations from CSV file.
        """
        c = connection.cursor()
        df = pd.read_csv(locations_csv)

        if len(df) > 0:
            table = "rh_location"
            if self.test:
                table = 'tmp_location'
                c.execute(f"""
                    CREATE TABLE IF NOT EXISTS {table} (id INTEGER PRIMARY KEY AUTOINCREMENT, level, parent_id, code, name, original_name, type, lat, long, created_at, updated_at);
                """)

            df['Long'] = df['Long'].str.replace(',', '.').astype(float)
            df['Lat'] = df['Lat'].str.replace(',', '.').astype(float)

            df.to_sql('tmp_locs', connection, if_exists='replace', index=False)

            c.execute(f"""
            insert into {table} (level, parent_id, code, name, original_name, type, created_at, updated_at)
            VALUES (0, NULL, 'ALL', 'ALL', NULL, 'All', datetime('now'), datetime('now'))
            """)

            c.execute(f"""
            insert into {table} (level, parent_id, code, name, original_name, type, created_at, updated_at)
            select distinct 0 level, NULL parent, ADM0_PCODE code, ADM0_NA_EN name, ADM0_translation original_name, 'Country' type, datetime('now') created_at, datetime('now') updated_at from tmp_locs
            """)

            c.execute(f"""
            insert into {table} (level, parent_id, code, name, original_name, type, created_at, updated_at)
            select distinct 1 level, r.id as parent_id, ADM1_PCODE code, ADM1_NA_EN name, ADM1_translation original_name, 'Province' type, datetime('now') created_at, datetime('now') updated_at
            from tmp_locs t inner join {table} r ON r.code = t.ADM0_PCODE;
            """)

            c.execute(f"""
            insert into {table} (level, parent_id, code, name, type, lat, long, created_at, updated_at)
            select distinct 2 level, r.id as parent_id, ADM2_PCODE code, ADM2_NA_EN name, 'District' type, t.lat, t.long, datetime('now') created_at, datetime('now') updated_at
            from tmp_locs t inner join {table} r ON r.code = t.ADM1_PCODE;
            """)

            c.execute("DROP TABLE tmp_locs;")

    def import_clusters_from_csv(self, connection, clusters_csv):
        """
        Import updated clusters from CSV
        """
        c = connection.cursor()
        df = pd.DataFrame()
        df = pd.read_csv(clusters_csv)

        if len(df) > 0:
            table = "rh_cluster"

            df.to_sql('tmp_clusters', connection, if_exists='replace', index=False)

            try:
                c.execute(
                    f"""insert into {table}(old_code, code, old_title, title) select old_code, code, old_title, title from tmp_clusters""")
                c.execute("DROP TABLE tmp_clusters;")
            except Exception as e:
                connection.rollback()

    def import_beneficiary_types_from_csv(self, connection, beneficiary_type_csv):
        """
        Import beneficiary types from CSV
        """
        c = connection.cursor()
        df = pd.DataFrame()
        df = pd.read_csv(beneficiary_type_csv)

        if len(df) > 0:
            table = "rh_beneficiarytype"

            df.to_sql('tmp_beneficiarytype', connection, if_exists='replace', index=False)

            try:
                c.execute(
                    f"""
                        insert into 
                        {table}(name, code, description, start_date, end_date, old_id, location_id) 
                        select 
                        beneficiary_type_name, beneficiary_type_id, description, start_date, end_date, _id, (select id from rh_location where code = tmp_beneficiarytype.admin0pcode)
                        from tmp_beneficiarytype""")
                c.execute("DROP TABLE tmp_beneficiarytype;")
            except Exception as e:
                connection.rollback()

    def import_organizations_from_csv(self, connection, organizations_csv):
        """
        Import organizations from CSV
        """
        c = connection.cursor()
        df = pd.DataFrame()
        df = pd.read_csv(organizations_csv)

        if len(df) > 0:
            table = "rh_organization"

            df.to_sql('tmp_organization', connection, if_exists='replace', index=False)

            try:
                # TODO: Handle the Locations

                c.execute(
                    f"""
                        insert into 
                        {table}(name, code, type, created_at, updated_at, old_id, location_id) 
                        select 
                        organization_name, organization, organization_type, createdAt, updatedAt, _id , (select id from rh_location where code = tmp_organization.admin0pcode)
                        from tmp_organization

                    """)
                c.execute("DROP TABLE tmp_organization;")
            except Exception as e:
                connection.rollback()

    def import_donors_from_csv(self, connection, donors_csv):
        """
        Import Donors from CSV
        """
        c = connection.cursor()
        df = pd.DataFrame()
        df = pd.read_csv(donors_csv)

        if len(df) > 0:
            table = "rh_donor"

            df.to_sql('tmp_donor', connection, if_exists='replace', index=False)

            try:
                c.execute(
                    f"""
                        insert into 
                        {table}(code, name, start_date, end_date, old_id, location_id) 
                        select 
                        project_donor_id, project_donor_name, start_date, end_date, _id, (select id from rh_location where code = tmp_donor.admin0pcode)
                        from tmp_donor
                    """)
                c.execute("DROP TABLE tmp_donor;")
            except Exception as e:
                connection.rollback()

    def import_indicators_from_csv(self, connection, indicators_csv):
        """
        Import Indicators from CSV
        """
        c = connection.cursor()
        df = pd.DataFrame()
        df = pd.read_csv(indicators_csv)

        if len(df) > 0:
            table = "rh_indicator"

            df.to_sql('tmp_indicator', connection, if_exists='replace', index=False)

            try:
                c.execute(
                    f"""
                        insert into 
                        {table}(code, name, numerator, denominator, description) 
                        select 
                        indicator_id, indicator_name, Numerator, Denominator, Description
                        from tmp_indicator
                    """)
                c.execute("DROP TABLE tmp_indicator;")
            except Exception as e:
                connection.rollback()

    def import_users_from_csv(self, connection, users_csv):
        """
        Import Users from CSV
        """
        c = connection.cursor()

        df = pd.DataFrame()
        df = pd.read_csv(users_csv)

        if len(df) > 0:
            table = "auth_user"

            df.to_sql('tmp_accounts', connection, if_exists='replace', index=False)

            try:
                c.execute(
                    "select admin0pcode,cluster_id,name,organization_id,phone,position,skype,visits,username from tmp_accounts")
                profile_info = c.fetchall()
                c.execute("select createdAt,email,last_logged_in,password,status,username from tmp_accounts")
                users = c.fetchall()
                profiles_list = []
                for profile in profile_info:
                    profile = list(profile)
                    skype = profile[7]
                    if not skype:
                        profile[7] = None
                    country = profile[0]
                    cluster = profile[1]
                    organization = profile[3]
                    if country:
                        c.execute(f"select id from rh_location where code='{country}'")
                        location_id = c.fetchone()
                        if location_id:
                            profile[0] = location_id[0]
                        else:
                            profile[0] = None

                    if cluster:
                        c.execute(f"select id from rh_cluster where code='{cluster}' or old_code='{cluster}'")
                        cluster_id = c.fetchone()
                        if cluster_id:
                            profile[1] = cluster_id[0]
                        else:
                            profile[1] = None

                    if organization:
                        c.execute(f"select id from rh_organization where old_id='{organization}'")
                        organization_id = c.fetchone()
                        if organization_id:
                            profile[3] = organization_id[0]
                        else:
                            profile[3] = None

                    profile = tuple(profile)
                    profiles_list.append(profile)

                for user in users:
                    user = list(user)
                    status = user[4]
                    user.append(False)
                    user.append(False)
                    user.append('')
                    user.append('')

                    if status == 'active':
                        user[4] = True

                    if not user[5]:
                        continue

                    password = user[3]
                    if password:
                        user[3] = 'bcrypt$' + password

                    # user = ['NULL' if a==None else a for a in user]
                    user = tuple(user)
                    aquery = f"""
                            insert into 
                            {table}(date_joined, email, last_login, password, is_active, username, is_superuser, is_staff, last_name, first_name) 
                            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """

                    c.execute(aquery, user)
                    user_id = c.lastrowid

                    c.execute(f"select username from {table} where id={user_id}")
                    db_user = c.fetchone()

                    u_profile = next(item for item in profiles_list if db_user[0] in item)
                    profile_cluster_id = False
                    if u_profile:
                        u_profile = list(u_profile)
                        u_profile.pop(-1)
                        profile_cluster_id = u_profile.pop(1)
                        u_profile.append(user_id)
                        u_profile = tuple(u_profile)
                    pquery = f"""
                            insert into 
                            users_profile(country_id,name,organization_id,phone,position,skype,visits,user_id) 
                            values (?, ?, ?, ?, ?, ?, ?, ?)
                        """
                    c.execute(pquery, u_profile)
                    last_profile_id = c.lastrowid

                    if last_profile_id and profile_cluster_id:
                        alquery = f"""
                                    insert into 
                                    users_profile_clusters(profile_id, cluster_id) 
                                    values({last_profile_id}, {profile_cluster_id})
                                """
                        c.execute(alquery)

                c.execute("DROP TABLE tmp_accounts;")
            except Exception as e:
                print("***********IMPORT ERROR:************ ", e)
                connection.rollback()

    def import_activities_from_csv(self, connection, activities_csv):
        """
        Import Activities from CSV file.
        """
        # connection.row_factory = sqlite3.Row
        c = connection.cursor()

        df = pd.read_csv(activities_csv)
        df['fields'] = df['fields'].fillna('')

        # df['fields'] = df['fields'].apply(lambda x: json.loads(x) if isinstance(x, str) else json.loads(str(x)))

        if len(df) > 0:
            table = "rh_activity"

            df.to_sql('tmp_activity', connection, if_exists='replace', index=False)

            try:
                c.execute(
                    "select active, activity_date, HRP_Code, Core_Indicator_Yes_No, code, name, subdomain_code, subdomain_name, start_date, end_date, _id, admin0pcode, cluster_id, indicator_id from tmp_activity")
                activities = c.fetchall()
                for activity in activities:
                    activity = list(activity)
                    active = activity[0]
                    if active == None:
                        activity[0] = True

                    indicator = activity[-1]
                    if indicator:
                        c.execute(f"select id from rh_indicator where code='{indicator}'")
                        indicator = c.fetchone()
                        if indicator:
                            activity[-1] = indicator[0]

                    cluster = activity.pop(-2)
                    location = activity.pop(-2)
                    activity = tuple(activity)

                    aquery = f"""
                            insert into 
                            {table}(active, activity_date, hrp_code, code_indicator, code, name, subdomain_code, subdomain_name, start_date, end_date, old_id, indicator_id) 
                            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """

                    c.execute(aquery, activity)
                    activity_id = c.lastrowid

                    lquery = f"""select id from rh_location where code='{location}'"""
                    c.execute(lquery)

                    location_id = c.fetchone()

                    if activity_id and location_id:
                        alquery = f"""
                            insert into 
                            rh_activity_locations(activity_id, location_id) 
                            values({activity_id}, {location_id[0]})
                        """
                        c.execute(alquery)

                    cquery = f"""select id from rh_cluster where code='{cluster}' or old_code='{cluster}'"""
                    c.execute(cquery)

                    cluster_id = c.fetchone()

                    if activity_id and cluster_id:
                        alquery = f"""
                            insert into 
                            rh_activity_clusters(activity_id, cluster_id) 
                            values({activity_id}, {cluster_id[0]})
                        """
                        c.execute(alquery)

                c.execute("DROP TABLE tmp_activity;")
            except Exception as e:
                connection.rollback()


importer = DataImporter(test=TEST)

# mongo_client = importer.get_mongo_client()

connection = importer.get_sqlite_client(SQLITEDB_PATH)
# connection = importer.get_postgres_client(SQLITEDB_PATH)

# Use Collections for import
# ngmHealthCluster = mongo_client.ngmHealthCluster
# ngmReportHub = mongo_client.ngmReportHub

# Try to import the data from different sources.
try:
    importer.import_currencies_from_csv(connection, CURRENCIES_CSV)

    importer.import_locations(connection, LOCATIONS_CSV)

    importer.import_clusters_from_csv(connection, CLUSTERS_CSV)

    importer.import_beneficiary_types_from_csv(connection, BENEFICIARY_TYPES_CSV)

    importer.import_organizations_from_csv(connection, ORGANIZATIONS_CSV)

    importer.import_donors_from_csv(connection, DONORS_CSV)

    importer.import_indicators_from_csv(connection, INDICATORS_CSV)

    importer.import_activities_from_csv(connection, ACTIVITIES_CSV)

    importer.import_users_from_csv(connection, USERS_CSV)

    connection.commit()

except Exception as e:

    print("***********IMPORT ERROR:************ ", e)
    print("***********Traceback:************ ", traceback.format_exc())
    print("***********Roll Back The Commits************ ")
    connection.rollback()

connection.close()
