from pymongo import MongoClient
from datetime import datetime
import sqlite3
import pandas as pd
import traceback


TEST = False   # set to False if working with test database and provide sqlite3 database

# SET THE FILE PATHS
SQLITEDB_PATH = 'rh/db.sqlite3'
# SQLITEDB_PATH = 'rh/scripts/testdb.sqlite3'
COUNTRIES_CSV = 'rh/scripts/countries.csv'
LOCATIONS_CSV = 'rh/scripts/af_loc.csv'
CLUSTERS_CSV = 'rh/scripts/updated_clusters.csv'

# Test project id 58e9c5dd97302c316d0f816b

class MongoToSqlite():
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


    def clean_org(self, value): 
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

        return value


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


    def import_countries(self, connection, countries_csv):
        """
        Import countries from CSV file.
        """

        c = connection.cursor()
        df = pd.DataFrame()
        df = pd.read_csv(countries_csv)

        if len(df)>0:
            table = "rh_country"
            if self.test:
                table = 'tmp_country'

                c.execute(f"CREATE TABLE IF NOT EXISTS {table} (id INTEGER PRIMARY KEY AUTOINCREMENT, name, code, code2)")
                
            df.to_sql('tmp_countries', connection, if_exists='replace', index=False)

            try:
                c.execute(f"""insert into {table} select rowid, Name, Code, Code2 from tmp_countries """)
                c.execute("DROP TABLE tmp_countries;")
            except Exception as e:
                connection.rollback()

            # connection.commit()
    
    def import_locations(self, connection, locations_csv):
        """
        Import locations from CSV file.
        """
        c = connection.cursor()
        df = pd.read_csv(locations_csv)

        if len(df)>0:
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


    def import_currencies(self, connection, mongodb):
        """
        Import Currencies from MongoDB
        """

        c = connection.cursor()
        currencies = list(mongodb.project.distinct("project_budget_currency"))
        key_map = {
            'project_budget_currency': 'name',
        }
        table = "rh_currency"

        t = list(zip([i+1 for i in range(len(currencies))], [c.upper() for c in currencies]))
        c.executemany("INSERT INTO {} VALUES (?,?)".format(table), t)


    def import_clusters(self, connection, mongodb):
        """
        Import clusters from MongoDB
        """
        clusters = list(mongodb.activities.find({}, {'cluster': 1, 'cluster_id': 1}))
        key_map = {
            'cluster_id': 'code',
            'cluster': 'title',
        }
        table = "rh_cluster"
        if self.test:
            table = 'tmp_cluster'

        self.build_tmp(connection, table, key_map, clusters)

    
    def import_clusters_from_csv(self, connection, clusters_csv):
        """
        Import updated clusters from CSV
        """
        c = connection.cursor()
        df = pd.DataFrame()
        df = pd.read_csv(clusters_csv)

        if len(df)>0:
            table = "rh_cluster"
            
            df.to_sql('tmp_clusters', connection, if_exists='replace', index=False)

            try:
                c.execute(f"""insert into {table} select rowid, code, title, old_code, old_title from tmp_clusters""")
                c.execute("DROP TABLE tmp_clusters;")
            except Exception as e:
                connection.rollback()
    

    def import_organizations(self, connection, mongodb):
        """
        Import organizations from MongoDB
        """
        organizations = list(mongodb.organizations.find({}, {'organization_name': 1, 'organization': 1, 'organization_type': 1}))
        key_map = {
            'organization_name': 'name',
            'organization': 'code',
            'organization_type': 'type',
        }

        table = "rh_organization"
        if self.test:
            table = 'tmp_organization'

        self.build_tmp(connection, table, key_map, organizations)


    def import_doners(self, connection, mongodb):

        """
        Import Users from MongoDB
        """
        c = connection.cursor()
        doners = list(mongodb.donors.find({}, 
        {'admin0pcode': 1, 
        'cluster_id': 1, 
        'project_donor_id': 1, 
        'project_donor_name': 1, 
        }))
        key_map = {
            'project_donor_id': 'project_donor_id',
            'project_donor_name': 'project_donor_name',
            'cluster_id': 'cluster_id',         
            'admin0pcode': 'country_id',         
        }
        table = "rh_doner"
            
        for doner in doners:
                    
            cluster_id = doner.get('cluster_id', None)
            country_code = doner.get('admin0pcode', None)

            if cluster_id and cluster_id == 'all':
                cluster_id = False
                doner.pop('cluster_id')
                
            if country_code == 'COL':
                country_code = 'CO'
            if country_code == 'ALL':
                country_code = None
                doner.pop('admin0pcode')
            
            if cluster_id:
                query = "SELECT rowid FROM rh_cluster WHERE old_code = '{}'".format(cluster_id)
                try:
                    c.execute(query)
                    cluster_id = c.fetchone()
                    if cluster_id:
                        doner.update({'cluster_id': cluster_id[0]})

                except Exception as e:
                    print("***********IMPORT ERROR in Fetching Cluster Code************ ", e)
                    print("***********Rool Backing Please Wait:************ ")
                    connection.rollback()

            if country_code:
                query = "SELECT rowid FROM rh_country WHERE code = '{}'".format(country_code.upper())
                try:
                    c.execute(query)
                    country_id = c.fetchone()
                    if country_id:
                        doner.update({'admin0pcode': country_id[0]})

                except Exception as e:
                    print("***********IMPORT ERROR in Importing Organization Code************ ", e)
                    print("***********Rool Backing Please Wait:************ ")
                    connection.rollback()

            
        self.build_tmp(connection, table, key_map, doners)


    ############ Import Users from mongoDB with relational data ############
    def import_users(self, connection, mongodb):
        """
        Import Users from MongoDB
        """
        c = connection.cursor()
        users = list(mongodb.user.find({}, 
        {'organization': 1, 
        'cluster_id': 1, 
        'name': 1, 
        'username': 1, 
        'email': 1, 
        'phone': 1, 
        'position': 1, 
        'status': 1, 
        'password': 1,
        'createdAt': 1,
        'visits': 1
        }))
        key_map = {
            'username': 'username',
            'email': 'email',
            'password': 'password',
            'is_superuser': 'is_superuser',
            'is_staff': 'is_staff',
            'phone': 'phone',
            'name': 'name',
            'visits': 'visits',
            'position': 'position',
            'status': 'is_active',
            'createdAt': 'date_joined',
            'cluster_id': 'cluster_id',
            'organization': 'organization_id',
            
        }
        table = "accounts_account"
        usernames = []
        for index, user in enumerate(users):
            status = False
            username = user.get('username', False)
            if username:
                if username in usernames:
                    del users[index]
                    continue
                else:
                    usernames.append(username)
            if user.get('status', False) and user.get('status', False) == 'active':
                status = True

            user['status'] = status
            user['is_superuser'] = False
            user['is_staff'] = False
            user['password'] = 'bcrypt$' + user['password']
            
        for u in users:
            if 'is_superuser' not in u:
                u.update({'is_superuser':  False})
            if 'is_staff' not in u:
                u.update({'is_staff':  False})
            else:
                u['is_staff'] = False
            
            cluster_code = u.get('cluster_id', False)
            organization_code = u.get('organization', False)
            
            if cluster_code:
                query = "SELECT rowid FROM rh_cluster WHERE old_code = '{}'".format(cluster_code)
                try:
                    c.execute(query)
                    cluster_id = c.fetchone()
                    if cluster_id:
                        if 'cluster_id' in u:
                            u['cluster_id'] = cluster_id[0]
                        else:
                            u.update({'cluster_id': cluster_id[0]})
                    else:
                        u.pop('cluster_id')

                except Exception as e:
                    print("***********IMPORT ERROR in Fetching Cluster Code************ ", e)
                    print("***********Rool Backing Please Wait:************ ")
                    connection.rollback()

            if organization_code:
                query = "SELECT rowid FROM rh_organization WHERE code = '{}'".format(organization_code)
                try:
                    c.execute(query)
                    organization_id = c.fetchone()
                    if organization_id:
                        if 'organization' in u:
                            u['organization'] = organization_id[0]
                        else:
                            u.update({'organization': organization_id[0]})
                    else:
                        u.pop('organization')

                except Exception as e:
                    print("***********IMPORT ERROR in Importing Organization Code************ ", e)
                    print("***********Rool Backing Please Wait:************ ")
                    connection.rollback()

            
        self.build_tmp(connection, table, key_map, users)


    ############ Import Activities from CSV with relational data ############
    def import_activities_from_csv(self, connection, mongodb):
        """
        Import countries from CSV file.
        """
        connection.row_factory = sqlite3.Row
        c = connection.cursor()

        df_rh = pd.read_csv('rh/scripts/test_activity.csv')
        df_ocha = pd.read_csv('rh/scripts/test_ocha.csv')

        if len(df_rh)>0 and len(df_ocha)>0:
            table = "rh_activity"
            if self.test:
                table = 'tmp_activity'
                c.execute(f"CREATE TABLE IF NOT EXISTS {table} (id INTEGER PRIMARY KEY AUTOINCREMENT, active, ocha_code, title, clusters, indicator, description, countries, fields default NULL, created_at, updated_at)")

            df_rh.to_sql('tmp_rh_activity', connection, if_exists='replace', index=False)
            df_ocha.to_sql('tmp_ocha_activity', connection, if_exists='replace', index=False)

            import json;
            

            d = json.dumps({'s':1})
            c.execute("""ALTER TABLE tmp_rh_activity ADD fields JSON DEFAULT '{}'""".format(d))

            rh_data = c.execute("""SELECT ocha_code,active,activity_description_name,activity_type_name,admin0pcode,cluster,cluster_id,indicator_name from tmp_rh_activity""")
            for record in rh_data.fetchall():
                ocha_data = c.execute("""SELECT * from tmp_ocha_activity""")
                record = dict(record)
                ocha_record = next((item for item in ocha_data.fetchall() if record['ocha_code'] == dict(item)['code']), None)
                if ocha_record:
                    ocha_ind = dict(ocha_record)['Indicator']
                c.execute(f"""insert into {table}(active, ocha_code, title, indicator) values (?, ?, ?, ?)""",
                        (
                            record['active'],
                            record['ocha_code'],
                            record['activity_description_name'],
                            ocha_ind,
                        ),
                )
                activity_id = c.lastrowid

                # Add Clusters
                many2many_cluster_table = 'rh_activity_clusters'
                related_cluster_table = 'rh_cluster'
                if self.test:
                    many2many_cluster_table = 'tmp_activity_clusters'
                    related_cluster_table = 'tmp_cluster'
                    query = f"CREATE TABLE IF NOT EXISTS {many2many_cluster_table}(activity_id INTEGER, cluster_id INTEGER)"
                    try:
                        c.execute(query)
                    except Exception as e:
                        print("***********IMPORT ERROR:************ ", e)
                        print("***********Rool Backing Please Wait:************ ")
                        connection.rollback()
                
                clusters = [a.strip() for a in record['cluster_id'].split(",")]

                q = f"""INSERT INTO {many2many_cluster_table}(activity_id, cluster_id) VALUES ({activity_id}, (SELECT rowid FROM {related_cluster_table} WHERE old_code IN (%s)))""" % ','.join('?' for i in clusters)
                try:
                    c.execute(q, clusters)
                except Exception as e:
                    print("***********IMPORT ERROR:************ ", e)
                    print("***********Rool Backing Please Wait:************ ")
                    connection.rollback()

                # Add Countries
                many2many_country_table = 'rh_activity_countries'
                related_country_table = 'rh_country'
                if self.test:
                    many2many_country_table = 'tmp_activity_countries'
                    related_country_table = 'tmp_country'
                    query = f"CREATE TABLE IF NOT EXISTS {many2many_country_table}(activity_id INTEGER, country_id INTEGER)"
                    try:
                        c.execute(query)
                    except Exception as e:
                        print("***********IMPORT ERROR:************ ", e)
                        print("***********Rool Backing Please Wait:************ ")
                        connection.rollback()
                

                countries = [a.strip() for a in record['admin0pcode'].split(",")]
                for country in countries:
                    if country in ["XX", "CB"]:
                        continue
                    if country == "UR":
                        country = "UY"
                    q = f"""INSERT INTO {many2many_country_table}(activity_id, country_id) VALUES ({activity_id}, (SELECT rowid FROM {related_country_table} WHERE code == '{country}' OR code2 == '{country}'))"""
                    try:
                        c.execute(q)
                    except Exception as e:
                        print("***********IMPORT ERROR:************ ", e)
                        print("***********Rool Backing Please Wait:************ ")
                        connection.rollback()

            c.execute("DROP TABLE tmp_rh_activity;")
            c.execute("DROP TABLE tmp_ocha_activity;")


    ############ Import Activities from mongoDB with relational data ############
    def import_activities(self, connection, mongodb):
        """
        Import activities from MongoDB
        """
        activities = list(mongodb.activities.find(
                {'start_date': 
                    {
                        '$gte': '2020-01-01'
                    }
                },
                {'active': 1, 'indicator_name': 1, 'activity_description_name': 1, 'activity_type_name': 1, 'activity_detail_name': 1, 'cluster': 1, 'admin0pcode': 1, 'cluster_id': 1}
            )
        )
        key_map = {
            'activity_type_name': 'title',
            'indicator_name': 'indicator',
            'activity_description_name': 'description',
            'activity_detail_name': 'detail',
            'active': 'active',
        }

        table = "rh_activity"
        if self.test:
            table = 'tmp_activity'

        activity_rows = self.build_tmp(connection, table, key_map, activities)
        
        # Add Clusters
        c = connection.cursor()
        many2many_cluster_table = 'rh_activity_clusters'
        related_cluster_table = 'rh_cluster'
        if self.test:
            many2many_cluster_table = 'tmp_activity_clusters'
            related_cluster_table = 'tmp_cluster'
            query = f"CREATE TABLE IF NOT EXISTS {many2many_cluster_table}(activity_id INTEGER, cluster_id INTEGER)"
            try:
                c.execute(query)
            except Exception as e:
                print("***********IMPORT ERROR:************ ", e)
                print("***********Rool Backing Please Wait:************ ")
                connection.rollback()
        
        
        for activity in activity_rows:
            activity_dict = next(item for item in activities if str(item['_id']) == activity[list(activity.keys())[0]][0])
            # clusters = tuple(a.strip() for a in activity_dict.get('cluster').split(","))
            clusters = [a.strip() for a in activity_dict.get('cluster_id').split(",")]

            q = f"""INSERT INTO {many2many_cluster_table}(activity_id, cluster_id) VALUES ({list(activity.keys())[0]}, (SELECT rowid FROM {related_cluster_table} WHERE old_code IN (%s)))""" % ','.join('?' for i in clusters)
            try:
                c.execute(q, clusters)
            except Exception as e:
                print("***********IMPORT ERROR:************ ", e)
                print("***********Rool Backing Please Wait:************ ")
                connection.rollback()
        
        # Add Countries
        many2many_country_table = 'rh_activity_countries'
        related_country_table = 'rh_country'
        if self.test:
            many2many_country_table = 'tmp_activity_countries'
            related_country_table = 'tmp_country'
            query = f"CREATE TABLE IF NOT EXISTS {many2many_country_table}(activity_id INTEGER, country_id INTEGER)"
            try:
                c.execute(query)
            except Exception as e:
                print("***********IMPORT ERROR:************ ", e)
                print("***********Rool Backing Please Wait:************ ")
                connection.rollback()
        
        for activity in activity_rows:
            activity_dict = next(item for item in activities if str(item['_id']) == activity[list(activity.keys())[0]][0])

            countries = [a.strip() for a in activity_dict.get('admin0pcode').split(",")]
            for country in countries:
                if country in ["XX", "CB"]:
                    continue
                if country == "UR":
                    country = "UY"
                q = f"""INSERT INTO {many2many_country_table}(activity_id, country_id) VALUES ({list(activity.keys())[0]}, (SELECT rowid FROM {related_country_table} WHERE code == '{country}' OR code2 == '{country}'))"""
                try:
                    c.execute(q)
                except Exception as e:
                    print("***********IMPORT ERROR:************ ", e)
                    print("***********Rool Backing Please Wait:************ ")
                    connection.rollback()
    

    ############ Import Projects from mongoDB with relational data ############
    def import_projects(self, connection, mongodb):
        """
        Import projects from MongoDB
        """
        c = connection.cursor()
        projects = list(mongodb.project.find(
                {'project_start_date': 
                    {
                        '$gte': datetime(2022, 1, 1)
                    }
                },

                {
                    'username': 1, 
                    'project_code': 1, 
                    'project_title': 1, 
                    'project_description': 1, 
                    'project_start_date': 1, 
                    'project_end_date': 1, 
                    'project_budget': 1, 
                    'project_budget_currency': 1,
                    'createdAt': 1,
                    'updatedAt': 1,
                    'cluster_id': 1,
                    'inter_cluster_activities': 1,
                }
            )
        )
        key_map = {
            'project_code': 'code',
            'username': 'user_id',
            'project_title': 'title',
            'project_description': 'description',
            'project_start_date': 'start_date',
            'project_end_date': 'end_date',
            'project_budget': 'budget',
            'project_budget_currency': 'budget_currency_id',
            'createdAt': 'created_at',
            'updatedAt': 'updated_at',
            'active': 'active',
        }

        table = "rh_project"
        if self.test:
            table = 'tmp_project'

        for project in projects:
            
            project_user = project.get('username', False)
            if project_user:
                    query = "SELECT rowid FROM accounts_account WHERE username = '{}'".format(project_user)
                    try:
                        c.execute(query)
                        user_id = c.fetchone()
                        if user_id:
                            if 'username' in project:
                                project['username'] = user_id[0]
                            else:
                                project.update({'username': user_id[0]})
                        else:
                            if 'username' in project:
                                project['username'] = False
                            else:
                                project.update({'username': False})

                    except Exception as e:
                        print("***********IMPORT ERROR in User Foreign Key:************ ", e)
                        print("***********Rool Backing Please Wait:************ ")
                        connection.rollback()

            project_currency = project.get('project_budget_currency', False)
            if project_currency:
                    query = "SELECT rowid FROM rh_currency WHERE name = '{}'".format(project_currency.upper())
                    try:
                        c.execute(query)
                        currency_id = c.fetchone()
                        if currency_id:
                            if 'organization' in project:
                                project['project_budget_currency'] = currency_id[0]
                            else:
                                project.update({'project_budget_currency': currency_id[0]})
                        else:
                            if 'organization' in project:
                                project['project_budget_currency'] = False
                            else:
                                project.update({'project_budget_currency': False})

                    except Exception as e:
                        print("***********IMPORT ERROR in Currency Foreign Key:************ ", e)
                        print("***********Rool Backing Please Wait:************ ")
                        connection.rollback()
            project.update({'active': True})

        project_rows = self.build_tmp(connection, table, key_map, projects)
        
        # # Add Clusters
        # c = connection.cursor()
        # many2many_cluster_table = 'rh_activity_clusters'
        # related_cluster_table = 'rh_cluster'
        # if self.test:
        #     many2many_cluster_table = 'tmp_activity_clusters'
        #     related_cluster_table = 'tmp_cluster'
        #     query = f"CREATE TABLE IF NOT EXISTS {many2many_cluster_table}(activity_id INTEGER, cluster_id INTEGER)"
        #     try:
        #         c.execute(query)
        #     except Exception as e:
        #         print("***********IMPORT ERROR:************ ", e)
        #         print("***********Rool Backing Please Wait:************ ")
        #         connection.rollback()
        
        
        # for activity in activity_rows:
        #     activity_dict = next(item for item in projects if str(item['_id']) == activity[list(activity.keys())[0]][0])
        #     # clusters = tuple(a.strip() for a in activity_dict.get('cluster').split(","))
        #     clusters = [a.strip() for a in activity_dict.get('cluster_id').split(",")]

        #     q = f"""INSERT INTO {many2many_cluster_table}(activity_id, cluster_id) VALUES ({list(activity.keys())[0]}, (SELECT rowid FROM {related_cluster_table} WHERE code IN (%s)))""" % ','.join('?' for i in clusters)
        #     try:
        #         c.execute(q, clusters)
        #     except Exception as e:
        #         print("***********IMPORT ERROR:************ ", e)
        #         print("***********Rool Backing Please Wait:************ ")
        #         connection.rollback()
        
        # # Add Countries
        # many2many_country_table = 'rh_activity_countries'
        # related_country_table = 'rh_country'
        # if self.test:
        #     many2many_country_table = 'tmp_activity_countries'
        #     related_country_table = 'tmp_country'
        #     query = f"CREATE TABLE IF NOT EXISTS {many2many_country_table}(activity_id INTEGER, country_id INTEGER)"
        #     try:
        #         c.execute(query)
        #     except Exception as e:
        #         print("***********IMPORT ERROR:************ ", e)
        #         print("***********Rool Backing Please Wait:************ ")
        #         connection.rollback()
        
        # for activity in activity_rows:
        #     activity_dict = next(item for item in projects if str(item['_id']) == activity[list(activity.keys())[0]][0])

        #     countries = [a.strip() for a in activity_dict.get('admin0pcode').split(",")]
        #     for country in countries:
        #         if country in ["XX", "CB"]:
        #             continue
        #         if country == "UR":
        #             country = "UY"
        #         q = f"""INSERT INTO {many2many_country_table}(activity_id, country_id) VALUES ({list(activity.keys())[0]}, (SELECT rowid FROM {related_country_table} WHERE code == '{country}' OR code2 == '{country}'))"""
        #         try:
        #             c.execute(q)
        #         except Exception as e:
        #             print("***********IMPORT ERROR:************ ", e)
        #             print("***********Rool Backing Please Wait:************ ")
        #             connection.rollback()


migration = MongoToSqlite(test=TEST)

mongo_client = migration.get_mongo_client()

connection = migration.get_sqlite_client(SQLITEDB_PATH)

# Use Collections for import
ngmHealthCluster = mongo_client.ngmHealthCluster

ngmReportHub = mongo_client.ngmReportHub

# Try to import the data from different sources.
try:
    # Import Countries from CSV file
    migration.import_countries(connection, COUNTRIES_CSV)

    # # Import Locations from CSV file
    migration.import_locations(connection, LOCATIONS_CSV)

    migration.import_currencies(connection, ngmHealthCluster)

    # migration.import_clusters(connection, ngmHealthCluster)

    migration.import_clusters_from_csv(connection, CLUSTERS_CSV)

    migration.import_organizations(connection, ngmReportHub)

    migration.import_doners(connection, ngmHealthCluster)

    migration.import_users(connection, ngmReportHub)

    migration.import_activities(connection, ngmHealthCluster)
    
    # migration.import_activities_from_csv(connection, ngmHealthCluster)

    migration.import_projects(connection, ngmHealthCluster)

    connection.commit()

except Exception as e:
    
    print("***********IMPORT ERROR:************ ", e)
    print("***********Traceback:************ ", traceback.format_exc())
    print("***********Roll Back The Commits************ ")
    connection.rollback()

connection.close()
