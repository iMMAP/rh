import csv
import traceback
from datetime import datetime

import pandas as pd
import psycopg2
from dateutil import parser as date_parser
from sqlalchemy import create_engine

# SET THE DATABASE CONNECTION PARAMETERS
POSTGRES_DB_HOST = "localhost"
POSTGRES_DB_NAME = "rh"
POSTGRES_DB_USER = "postgres"
POSTGRES_DB_PASSWORD = "f4d11447"

# CSV DATA FILES
CURRENCIES_CSV = "./data/updated_nov_2023/currencies.csv"
LOCATIONS_CSV = "./data/updated_nov_2023/af_loc.csv"
CLUSTERS = "./data/updated_nov_2023/clusters.csv"
INDICATORS_CSV = "./data/updated_nov_2023/indicators.csv"
ACTIVITY_DOMAIN_CSV = "./data/updated_nov_2023/activity_domains.csv"
ACTIVITY_DESCRIPTION_CSV = "./data/updated_nov_2023/activity_types.csv"
ACTIVITY_DETAIL_CSV = "./data/updated_nov_2023/activity_details.csv"
BENEFICIARY_TYPES_CSV = "./data/updated_nov_2023/beneficiary_types.csv"
ORGANIZATIONS_CSV = "./data/updated_nov_2023/organizations.csv"
DONORS_CSV = "./data/updated_nov_2023/donors.csv"
USERS_CSV = "./data/updated_nov_2023/user.csv"
FACILITIES = "./data/updated_nov_2023/facility_site_types.csv"
DISS_CSV = "./data/updated_nov_2023/dissaggregation.csv"
STOCKUNIT_CSV = "./data/updated_nov_2023/stockunits.csv"
STOCKITEMS_TYPES_CSV = "./data/updated_nov_2023/stockitems_types.csv"

def get_postgres_client(host, dbname, user, password):
    """
    Returns a PostgreSQL connection instance.
    """
    conn_string = f"host={host} dbname={dbname} user={user} password={password}"
    return psycopg2.connect(conn_string)


def parse_date(date_str):
    try:
        # Parse the date string using dateutil.parser
        date_obj = date_parser.parse(date_str)
        return date_obj.date()
    except ValueError:
        # If parsing fails, return None or handle the error as needed
        return None


def import_currencies_from_csv(conn, currencies_csv):
    """
    Import Currencies from CSV
    """
    c = conn.cursor()
    df = pd.read_csv(currencies_csv)

    if len(df) > 0:
        table = "rh_currency"

        # Create a temporary table to hold CSV data
        c.execute(f"CREATE TEMP TABLE tmp_currency (name VARCHAR);")

        # Load CSV data into the temporary table
        with conn.cursor() as cursor:
            copy_sql = f"""
                COPY tmp_currency(name)
                FROM stdin WITH CSV HEADER DELIMITER ','
            """
            cursor.copy_expert(sql=copy_sql, file=open(currencies_csv, "r"))

        # Merge data from temporary table into the main table
        try:
            c.execute(f"INSERT INTO {table}(name) SELECT name FROM tmp_currency;")
        except Exception as exception:
            conn.rollback()
            raise exception
        finally:
            # Drop the temporary table
            c.execute("DROP TABLE IF EXISTS tmp_currency;")


def import_stock_units_from_csv(conn, stockunits_csv):
    """
    Import Stock Unit from CSV
    """
    c = conn.cursor()
    df = pd.read_csv(stockunits_csv)

    if len(df) > 0:
        table = "stock_stockunit"

        # Create a temporary table to hold CSV data
        c.execute(f"CREATE TEMP TABLE tmp_stockunit (name VARCHAR);")

        # Load CSV data into the temporary table
        with conn.cursor() as cursor:
            copy_sql = f"""
                COPY tmp_stockunit(name)
                FROM stdin WITH CSV HEADER DELIMITER ','
            """
            cursor.copy_expert(sql=copy_sql, file=open(stockunits_csv, "r"))

        # Merge data from temporary table into the main table
        try:
            c.execute(f"INSERT INTO {table}(name) SELECT name FROM tmp_stockunit;")
        except Exception as exception:
            conn.rollback()
            raise exception
        finally:
            # Drop the temporary table
            c.execute("DROP TABLE IF EXISTS tmp_stockunit;")


def import_stockitems_types_from(conn, stockitems_types_csv):
    """
    Import Stock Items types from CSV
    """
    c = conn.cursor()
    df = pd.read_csv(stockitems_types_csv)

    if len(df) > 0:
        table = "stock_stockitemstype"

        # Create a temporary table to hold CSV data
        c.execute(f"CREATE TEMP TABLE tmp_stockitemstype (old_id VARCHAR, cluster_id VARCHAR, name VARCHAR);")

        # Load CSV data into the temporary table
        with conn.cursor() as cursor:
            copy_sql = f"""
                COPY tmp_stockitemstype(old_id, cluster_id, name)
                FROM stdin WITH CSV HEADER DELIMITER ','
            """
            cursor.copy_expert(sql=copy_sql, file=open(stockitems_types_csv, "r"))

        # Merge data from temporary table into the main table
        try:
            c.execute(f"""
                INSERT INTO {table}(old_id, cluster_id, name)
                SELECT old_id, cluster_id, name FROM tmp_stockitemstype
            """)
        except Exception as exception:
            print(exception)
            conn.rollback()
            return

        # Update cluster_id based on the corresponding cluster's ID
        try:
            c.execute("""
                UPDATE stock_stockitemstype AS s
                SET cluster_id = c.id
                FROM rh_cluster AS c
                WHERE s.cluster_id = c.code
            """)
        except Exception as e:
            print(f"Error in stockitem_types and cluster: {e}")
            conn.rollback()
            return

        # Drop the temporary table
        c.execute("DROP TABLE IF EXISTS tmp_stockitemstype;")


def import_locations(conn, locations_csv):
    """
    Import locations from CSV file into PostgreSQL database.
    """
    c = conn.cursor()

    # Create temporary table
    c.execute("""
        CREATE TEMP TABLE tmp_locs (
            ADM0_PCODE VARCHAR,
            ADM0_NA_EN VARCHAR,
            ADM0_translation VARCHAR,
            ADM1_PCODE VARCHAR,
            ADM1_NA_EN VARCHAR,
            ADM1_translation VARCHAR,
            ADM2_PCODE VARCHAR,
            ADM2_NA_EN VARCHAR,
            UNIT_TYPE VARCHAR,
            Lat FLOAT,
            Long FLOAT
        )
    """)
    
    with open(locations_csv, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Replace commas with dots and convert to float
            long_val = float(row['Long'].replace(',', '.'))
            lat_val = float(row['Lat'].replace(',', '.'))

            # Insert data into temporary table
            c.execute("""
                INSERT INTO tmp_locs (ADM0_PCODE, ADM0_NA_EN, ADM0_translation, ADM1_PCODE, ADM1_NA_EN, ADM1_translation, ADM2_PCODE, ADM2_NA_EN, UNIT_TYPE, Lat, Long)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (row['ADM0_PCODE'], row['ADM0_NA_EN'], row['ADM0_translation'], row['ADM1_PCODE'], row['ADM1_NA_EN'], row['ADM1_translation'], row['ADM2_PCODE'], row['ADM2_NA_EN'], row['UNIT_TYPE'], lat_val, long_val))

    # Insert statements adapted for PostgreSQL
    c.execute("""
        INSERT INTO rh_location (level, parent_id, code, name, original_name, type, created_at, updated_at)
        VALUES (0, %s, 'ALL', 'ALL', NULL, 'All', now(), now())
    """, (None,))

    c.execute("""
        INSERT INTO rh_location (level, parent_id, code, name, original_name, type, created_at, updated_at)
        SELECT DISTINCT 0 as level, CAST(NULL AS BIGINT) as parent, ADM0_PCODE as code, ADM0_NA_EN as name, 
        ADM0_translation as original_name, 'Country' as type, now() as created_at, now() as updated_at 
        FROM tmp_locs
    """)

    c.execute("""
        INSERT INTO rh_location (level, parent_id, code, name, original_name, type, created_at, updated_at)
        SELECT DISTINCT 1 as level, r.id as parent_id, ADM1_PCODE as code, ADM1_NA_EN as name, 
        ADM1_translation as original_name, 'Province' as type, now() as created_at, now() as updated_at
        FROM tmp_locs t 
        INNER JOIN rh_location r ON r.code = t.ADM0_PCODE
    """)

    c.execute("""
        INSERT INTO rh_location (level, parent_id, code, name, type, lat, long, created_at, updated_at)
        SELECT DISTINCT 2 as level, r.id as parent_id, ADM2_PCODE as code, ADM2_NA_EN as name, 'District' as type, 
        t.lat, t.long, now() as created_at, now() as updated_at
        FROM tmp_locs t 
        INNER JOIN rh_location r ON r.code = t.ADM1_PCODE
    """)

    # Drop the temporary table
    c.execute("DROP TABLE IF EXISTS tmp_locs;")


def import_clusters_from_csv(conn, clusters_csv):
    """
    Import updated clusters from CSV into PostgreSQL
    """
    c = conn.cursor()

    with open(clusters_csv, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        
        if reader.fieldnames:  # Check if CSV has data
            table = "rh_cluster"

            # Create a temporary table in the database
            c.execute("""
                CREATE TEMP TABLE tmp_clusters (
                    title VARCHAR,
                    code VARCHAR,
                    name VARCHAR
                )
            """)

            # Insert data from CSV into the temporary table
            for row in reader:
                c.execute("""
                    INSERT INTO tmp_clusters (title, code, name) VALUES (%s, %s, %s)
                """, (row['title'], row['code'], row['name']))

            try:
                # Insert data from temporary table into the target table
                c.execute("""
                    INSERT INTO {} (title, code, name)
                    SELECT title, code, name FROM tmp_clusters
                """.format(table))
                
                # Drop the temporary table after data insertion
                c.execute("DROP TABLE tmp_clusters;")
                
                # Commit the transaction
                conn.commit()
            except Exception as exception:
                # Rollback the transaction in case of any exception
                conn.rollback()
                print("Error:", exception)


def import_organizations_from_csv(conn, organizations_csv):
    """
    Import organizations from CSV into PostgreSQL
    """
    c = conn.cursor()

    with open(organizations_csv, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        if reader.fieldnames:  # Check if CSV has data
            table = "rh_organization"

            # Create a temporary table in the database
            c.execute("""
                CREATE TEMP TABLE tmp_organization (
                    _id VARCHAR,
                    createdAt TIMESTAMP,
                    organization VARCHAR,
                    organization_name VARCHAR,
                    organization_type VARCHAR,
                    updatedAt TIMESTAMP,
                    admin0pcode VARCHAR
                )
            """)

            # Insert data from CSV into the temporary table
            for row in reader:
                # Parse datetime strings and set time to 00:00:00
                created_at = parse_date(row['createdAt'])
                updated_at = parse_date(row['updatedAt'])
                
                c.execute("""
                    INSERT INTO tmp_organization (_id, createdAt, organization, organization_name, organization_type, updatedAt, admin0pcode)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    row['_id'], created_at, row['organization'], row['organization_name'], 
                    row['organization_type'], updated_at, row['admin0pcode']
                ))

            try:
                # Insert data from temporary table into the target table and handle related tables
                c.execute("""
                    INSERT INTO {} (old_id, created_at, code, name, type, updated_at)
                    SELECT _id, createdAt, organization, organization_name, organization_type, updatedAt
                    FROM tmp_organization
                """.format(table))

                # Drop the temporary table after data insertion
                c.execute("DROP TABLE tmp_organization;")
                
                # Commit the transaction
                conn.commit()
            except Exception as exception:
                # Rollback the transaction in case of any exception
                conn.rollback()
                print("exception: ", exception)


def import_donors_from_csv(conn, donors_csv):
    """
    Import Donors from CSV
    """
    c = conn.cursor()

    try:
        with open(donors_csv, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Extract data from the CSV row
                _id = row['_id']
                end_date = row['end_date']
                project_donor_id = row['project_donor_id']
                project_donor_name = row['project_donor_name']
                start_date = row['start_date']
                admin0pcode = row['admin0pcode']

                # Handle empty date values
                if not end_date:
                    end_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                else:
                    end_date = parse_date(row['end_date'])
                if not start_date:
                    start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                else:
                    start_date = parse_date(row['start_date'])

                # Insert data into the database
                c.execute("""
                    INSERT INTO rh_donor (old_id, updated_at, code, name, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (_id, end_date, project_donor_id, project_donor_name, start_date))

                # Fetch the last inserted donor id
                last_donor_id = c.lastrowid

                # Fetch the location id for the given country code
                c.execute("SELECT id FROM rh_location WHERE code = %s", (admin0pcode,))
                country_id = c.fetchone()

                # Insert into rh_donor_countries if donor id and country id are found
                if last_donor_id and country_id:
                    c.execute("""
                        INSERT INTO rh_donor_countries (donor_id, location_id)
                        VALUES (%s, %s)
                    """, (last_donor_id, country_id[0]))

    except Exception as exception:
        print(f"ERROR: donors: {exception}")
        conn.rollback()


def import_users_from_csv(conn, users_csv):
    """
    Import Users from CSV
    """
    c = conn.cursor()

    try:
        with open(users_csv, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Extract user data from the CSV row
                username = row['username']
                email = row['email']
                password = row['password']
                status = row['status']
                admin0pcode = row['admin0pcode']
                cluster_id = row['cluster_id']
                organization_id = row['organization_id']
                phone = row['phone']
                position = row['position']
                skype = row['skype']
                created_at = row['createdAt']
                last_logged_in = row['last_logged_in']

                # Convert created_at and last_logged_in to datetime if not empty
                if created_at:
                    created_at = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
                if last_logged_in:
                    last_logged_in = datetime.strptime(last_logged_in, '%Y-%m-%dT%H:%M:%S.%fZ')

                # Handle status
                is_active = True if status == "active" else False

                # Append False values for extra columns
                user_info = [created_at, email, last_logged_in, password, is_active, username, False, False, '', '']

                # Insert user data into auth_user table
                c.execute("""
                    INSERT INTO auth_user (date_joined, email, last_login, password, is_active, username, 
                    is_superuser, is_staff, last_name, first_name) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, user_info)

                # Fetch the last inserted user id
                user_id = c.lastrowid

                # Insert profile data into users_profile table
                c.execute("""
                    INSERT INTO users_profile (country_id, organization_id, phone, position, skype, user_id, 
                    is_cluster_contact) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (admin0pcode, organization_id, phone, position, skype, user_id, False))

                # Fetch the last inserted profile id
                profile_id = c.lastrowid

                # Fetch cluster id based on the cluster name or code
                if cluster_id:
                    if cluster_id in ["coordination", "smsd"]:
                        cluster_id = "cccm"
                    if cluster_id == "agriculture":
                        cluster_id = "fsac"
                    if cluster_id == "rnr_chapter":
                        cluster_id = "protection"
                    c.execute("""
                        SELECT id FROM rh_cluster WHERE code = %s OR title = %s OR name = %s
                    """, (cluster_id, cluster_id, cluster_id))
                    cluster_id = c.fetchone()

                    # Insert into users_profile_clusters if cluster id is found
                    if cluster_id:
                        c.execute("""
                            INSERT INTO users_profile_clusters (profile_id, cluster_id) 
                            VALUES (%s, %s)
                        """, (profile_id, cluster_id[0]))

    except Exception as exception:
        print("***********IMPORT ERROR - USER ************ ", exception)
        conn.rollback()


connection = get_postgres_client(POSTGRES_DB_HOST, POSTGRES_DB_NAME, POSTGRES_DB_USER, POSTGRES_DB_PASSWORD)

# Try to import the data from different sources.
try:
    # import_currencies_from_csv(connection, CURRENCIES_CSV)

    # import_locations(connection, LOCATIONS_CSV)

    # import_clusters_from_csv(connection, CLUSTERS)

    # import_organizations_from_csv(connection, ORGANIZATIONS_CSV)

    # import_donors_from_csv(connection, DONORS_CSV)

    import_users_from_csv(connection, USERS_CSV)

    # import_facilities_from_csv(connection, FACILITIES)

    # import_beneficiary_types_from_csv(connection,BENEFICIARY_TYPES_CSV)

    # import_dissaggregation_from_csv(connection,DISS_CSV)

    # import_stock_units_from_csv(connection, STOCKUNIT_CSV)

    # import_stockitems_types_from(connection, STOCKITEMS_TYPES_CSV)

    connection.commit()

except Exception as exc:
    print("***********IMPORT ERROR:************ ", exc)
    print("***********Traceback:************ ", traceback.format_exc())
    print("***********Roll Back The Commits************ ")
    connection.rollback()

finally:
    connection.close()
