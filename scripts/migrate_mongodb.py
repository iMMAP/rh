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
                str_cols = str_cols.replace('_id,', '')
            query = f"INSERT INTO {tbl}({str_cols}) VALUES ({str_sql_val})"

            cursor.execute(query, entity)

            if not self.test:
                entity.insert(0, _id)
            rows.append({cursor.lastrowid: entity})

        # query = f'INSERT INTO {tbl} ({str_cols}) VALUES ({str_sql_val})'
        # con.executemany(query, entities)
        # con.commit()
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

            # connection.commit()

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

                q = f"""INSERT INTO {many2many_cluster_table}(activity_id, cluster_id) VALUES ({activity_id}, (SELECT rowid FROM {related_cluster_table} WHERE code IN (%s)))""" % ','.join('?' for i in clusters)
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
                {}, 
                {'active': 1, 'indicator_name': 1, 'activity_description_name': 1, 'activity_type_name': 1, 'cluster': 1, 'admin0pcode': 1, 'cluster_id': 1}
            )
        )
        key_map = {
            'activity_type_name': 'title',
            'indicator_name': 'indicator',
            'activity_description_name': 'description',
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

            q = f"""INSERT INTO {many2many_cluster_table}(activity_id, cluster_id) VALUES ({list(activity.keys())[0]}, (SELECT rowid FROM {related_cluster_table} WHERE code IN (%s)))""" % ','.join('?' for i in clusters)
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

    migration.import_clusters(connection, ngmHealthCluster)

    migration.import_organizations(connection, ngmReportHub)

    # migration.import_activities(connection, ngmHealthCluster)
    migration.import_activities_from_csv(connection, ngmHealthCluster)
    connection.commit()

except Exception as e:
    
    print("***********IMPORT ERROR:************ ", e)
    print("***********Traceback:************ ", traceback.format_exc())
    print("***********Roll Back The Commits************ ")
    connection.rollback()

connection.close()
