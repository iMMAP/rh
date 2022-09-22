from pymongo import MongoClient
from datetime import datetime
import sqlite3
import pandas as pd


TEST = True   # set to False if working with test database and provide sqlite3 database

# SET THE FILE PATHS
SQLITEDB_PATH = 'testdb.sqlite3'
COUNTRIES_CSV = 'countries.csv'
LOCATIONS_CSV = 'af_loc.csv'

class MigrateDatabaseToSqlite():
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
                if x.get('cluster') in [e[1] for e in entities]:
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
        con.commit()
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
        df = pd.read_csv(countries_csv)
        df.to_sql('tmp_countries', connection, index=False)
        table = "rh_country"
        
        if self.test:
            table = 'tmp_country'
            connection.execute(f"CREATE TABLE {table} (id INTEGER PRIMARY KEY AUTOINCREMENT, name, code)")
            
        connection.execute(f"""insert into {table} select rowid, Name, Code from tmp_countries """)
        connection.execute("DROP TABLE tmp_countries;")

        connection.commit()
    
    def import_locations(self, connection, locations_csv):
        """
        Import locations from CSV file.
        """
        df = pd.read_csv(locations_csv)

        df['Long'] = df['Long'].str.replace(',', '.').astype(float)
        df['Lat'] = df['Lat'].str.replace(',', '.').astype(float)

        df.to_sql('tmp_locs', connection, index=False)

        table = "rh_location"

        if self.test:
            table = 'tmp_location'
            connection.execute(f"""
                CREATE TABLE {table} (id INTEGER PRIMARY KEY AUTOINCREMENT, level, parent_id, code, name, original_name, type, lat, long, created_at, updated_at);
            """)

        connection.execute(f"""
        insert into {table} (level, parent_id, code, name, original_name, type, created_at, updated_at)
        select distinct 0 level, NULL parent, ADM0_PCODE code, ADM0_NA_EN name, ADM0_translation original_name, 'country' type, datetime('now') created_at, datetime('now') updated_at from tmp_locs
        """)

        connection.execute(f"""
        insert into {table} (level, parent_id, code, name, original_name, type, created_at, updated_at)
        select distinct 1 level, r.id as parent_id, ADM1_PCODE code, ADM1_NA_EN name, ADM1_translation original_name, 'province' type, datetime('now') created_at, datetime('now') updated_at
        from tmp_locs t inner join {table} r ON r.code = t.ADM0_PCODE;
        """)

        connection.execute(f"""
        insert into {table} (level, parent_id, code, name, type, lat, long, created_at, updated_at)
        select distinct 2 level, r.id as parent_id, ADM2_PCODE code, ADM2_NA_EN name, 'district' type, t.lat, t.long, datetime('now') created_at, datetime('now') updated_at
        from tmp_locs t inner join {table} r ON r.code = t.ADM1_PCODE;
        """)

        connection.execute("DROP TABLE tmp_locs;")
        connection.commit()

    def import_clusters(self, connection, mongodb):
        """
        Import clusters from MongoDB
        """
        clusters = list(mongodb.beneficiaries.find({}, {'cluster': 1}))
        key_map = {
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

    def import_activities(self, connection, mongodb):
        """
        Import activities from MongoDB
        """
        activities = list(mongodb.activities.find(
                {}, 
                {'active': 1, 'activity_description_name': 1, 'activity_type_name': 1, 'cluster': 1, 'admin0pcode': 1}
            ).limit(5)
        )
        key_map = {
            'activity_type_name': 'title',
            'activity_description_name': 'description',
            'active': 'active',
        }

        table = "rh_activity"
        if self.test:
            table = 'tmp_activity'

        activity_rows = self.build_tmp(connection, table, key_map, activities)

        # TODO: Handle relational data like ManyToMany, ForeignKey, etc.

        # many2many_table = 'rh_activity_clusters'
        # related_table = 'rh_cluster'
        # if self.test:
        #     many2many_table = 'tmp_activity_clusters'
        #     related_table = 'tmp_cluster'
        #     query = f"CREATE TABLE {many2many_table}(activity_id INTEGER, cluster_id INTEGER)"
        #     connection.execute(query)
        
        
        # for activity in activity_rows:
        #     activity_dict = next(item for item in activities if str(item['_id']) == activity[list(activity.keys())[0]][0])
        #     clusters = tuple(a.strip() for a in activity_dict.get('cluster').split(","))

        #     connection.execute(f"""INSERT INTO {many2many_table}(activity_id, cluster_id)
        #             SELECT ?, rowid
        #             FROM {related_table}
        #             WHERE title IN ?""",
        #         [list(activity.keys())[0], clusters])
        # connection.commit()


migration = MigrateDatabaseToSqlite(test=TEST)

mongo_client = migration.get_mongo_client()
connection = migration.get_sqlite_client(SQLITEDB_PATH)

# Use Collections for import
ngmHealthCluster = mongo_client.ngmHealthCluster
ngmReportHub = mongo_client.ngmReportHub

# Import Countries from CSV file
migration.import_countries(connection, COUNTRIES_CSV)

# # Import Locations from CSV file
migration.import_locations(connection, LOCATIONS_CSV)

migration.import_clusters(connection, ngmHealthCluster)

migration.import_organizations(connection, ngmReportHub)

migration.import_activities(connection, ngmHealthCluster)
