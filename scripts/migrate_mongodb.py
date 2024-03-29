import sqlite3
import traceback
from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine


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

connection = create_engine('postgresql://postgres:admin@localhost:5432/rh')
engine_connection = connection.raw_connection()
c = engine_connection.cursor()


def import_currencies_from_csv(conn, currencies_csv):
    """
    Import Currencies from CSV
    """
    
    df = pd.read_csv(currencies_csv)

    if len(df) > 0:
        table = "rh_currency"

        df.to_sql("tmp_currency", conn, if_exists="replace", index=False)

        try:
            c.execute(f"""insert into {table}(name,created_at, updated_at) select name,now(),now() from tmp_currency""")
            c.execute("DROP TABLE tmp_currency;")
        except Exception as exception:
            engine_connection.rollback()


def import_stock_units_from_csv(conn, stockunits_csv):
    """
    Import Stock Unit from CSV
    """
    
    df = pd.read_csv(stockunits_csv)

    if len(df) > 0:
        table = "stock_stockunit"

        df.to_sql("tmp_stockunit", conn, if_exists="replace", index=False)

        try:
            c.execute(f"""insert into {table}(name) select name from tmp_stockunit""")
            c.execute("DROP TABLE tmp_stockunit;")
        except Exception as exception:
            engine_connection.rollback()


def import_stockitems_types_from(conn, stockitems_types_csv):
    """
    Import Stock Items types from CSV
    """
    
    df = pd.read_csv(stockitems_types_csv)

    if len(df) > 0:
        table = "stock_stockitemstype"

        df.to_sql("tmp_stockitemstype", conn, if_exists="replace", index=False)

        try:
            c.execute(f"""insert into {table}(name) select stock_item_name from tmp_stockitemstype""")
        except Exception as exception:
            print("from insert",exception)
            engine_connection.rollback()


        try:
            c.execute('SELECT id,code FROM rh_cluster')
            cluster_ids = c.fetchall()

    
            c.execute('SELECT stock_item_name,cluster_id FROM tmp_stockitemstype')
            stock_itemstypes = c.fetchall()

            for cluster_id in cluster_ids:
                for stock_itemstype in stock_itemstypes:
                    if cluster_id[1] == stock_itemstype[1]:
                        c.execute('''
                        UPDATE stock_stockitemstype
                        SET cluster_id = %s
                        WHERE name = %s
                        ''', (cluster_id[0],stock_itemstype[0]))
        except Exception as e:
            print(f"Error in stockitem_types and cluster: {e}")
            engine_connection.rollback()
        
        c.execute("DROP TABLE tmp_stockitemstype;")

# c.execute(f"""insert into {table}(old_id, cluster_id,stock_items_name) select _id, cluster_id,stock_item_name from tmp_stockitemstype""")          

def import_locations(conn, locations_csv):
    """
    Import locations from CSV file.
    """
    df = pd.read_csv(locations_csv)

    if len(df) > 0:
        table = "rh_location"

        df["long"] = df["long"].str.replace(",", ".").astype(float)
        df["lat"] = df["lat"].str.replace(",", ".").astype(float)

        df.to_sql("tmp_locs", conn, if_exists="replace", index=False)

        c.execute(
            f"""
        insert into {table} (level, parent_id, code, name, original_name, type, created_at, updated_at)
        VALUES (0, NULL, 'ALL', 'ALL', NULL, 'All', now(), now())
        """
        )

        c.execute(
            f"""
        insert into {table} (level, code, name, original_name, type, created_at, updated_at)
        select distinct 0 "level", "adm0_pcode" as code, "adm0_na_en" as name, "adm0_translation" as original_name, 
        'Country' as type, now() as created_at, now() as updated_at 
        from tmp_locs
        """
        )

        c.execute(
            f"""
        INSERT INTO {table} (level, parent_id, code, name, original_name, type, created_at, updated_at)
        SELECT DISTINCT 
            1 AS level, 
            r.id AS parent_id, 
            "adm1_pcode" AS code, 
            "adm1_na_en" AS name, 
            "adm1_translation" AS original_name, 
            'Province' AS type, 
            NOW() AS created_at, 
            NOW() AS updated_at
        FROM 
            tmp_locs t 
        INNER JOIN 
            {table} r ON r.code = t.adm0_pcode;
        """
        )

        c.execute(
            f"""
        INSERT INTO {table} (level, parent_id, code, name, type, lat, long, created_at, updated_at)
        SELECT DISTINCT 
            2 AS level, 
            r.id AS parent_id, 
            "adm2_pcode" AS code, 
            "adm2_na_en" AS name, 
            'District' AS type, 
            CAST(t.Lat AS DOUBLE PRECISION) AS lat, 
            CAST(t.Long AS DOUBLE PRECISION) AS long, 
            NOW() AS created_at, 
            NOW() AS updated_at
        FROM 
            tmp_locs t
        INNER JOIN 
            {table} r ON r.code = t.adm1_pcode;
        """
        )

        c.execute("DROP TABLE tmp_locs;")


def import_clusters_from_csv(conn, clusters_csv):
    """
    Import updated clusters from CSV
    """
    
    df = pd.read_csv(clusters_csv)

    if len(df) > 0:
        table = "rh_cluster"

        df.to_sql("tmp_clusters", conn, if_exists="replace", index=False)

        try:
            c.execute(
                f"""insert into {table}(title, code, name,created_at,updated_at) select title, code, name,now(),now() from tmp_clusters"""
            )
            c.execute("DROP TABLE tmp_clusters;")
        except Exception as exception:
            engine_connection.rollback()


def import_indicators_from_csv(conn, indicators_csv):
    """
    Import Indicators from CSV
    """
    
    df = pd.read_csv(indicators_csv)

    if len(df) > 0:
        table = "rh_indicator"

        df.to_sql("tmp_indicator", conn, if_exists="replace", index=False)
        try:
            c.execute(
                "select activity_description_id,indicator_name from tmp_indicator"
            )
            indicators = c.fetchall()
            for indicator in indicators:
                indicator = list(indicator)
                activity_type = indicator[0]

                if activity_type:
                    c.execute(
                        f"select id from rh_activitytype where code='{activity_type}'"
                    )
                    activity_type_id = c.fetchone()
                    if activity_type_id:
                        activity_type = activity_type_id[0]
                    else:
                        activity_type = None

                indicator.pop(0)
                # indicator.append(None)
                # indicator.append(None)
                # indicator.append(None)

                aquery = f"""insert into {table}(name) 
                values (%s)
                """
                            
                try:
                    c.execute(aquery, indicator)
                except Exception as exception:
                    print(f"LOG Indicators: {exception}")
                    continue

                last_indicator_id = c.lastrowid

                if last_indicator_id and activity_type:
                    aquery = f"""
                        insert into 
                        rh_indicator_activity_types(indicator_id, activitytype_id) 
                        values({last_indicator_id}, {activity_type})
                    """
                    c.execute(aquery)

            c.execute("DROP TABLE tmp_indicator;")
        except Exception as exception:
            print(f"ERROR: import_indicators_from_csv: {exception}")
            engine_connection.rollback()


def import_activity_domains_from_csv(conn, activity_domain_csv):
    """
    Import updated clusters from CSV
    """
    
    df = pd.read_csv(activity_domain_csv)

    if len(df) > 0:
        table = "rh_activitydomain"

        df.to_sql("tmp_activitydomain", conn, if_exists="replace", index=False)

        try:
            c.execute(
                "select activity_type_id,activity_type_name,cluster_id from tmp_activitydomain"
            )
            activity_domains = c.fetchall()
            for domain in activity_domains:
                domain = list(domain)
                cluster = domain[2]
                country = "AF"

                if country:
                    c.execute(f"select id from rh_location where code='{country}'")
                    location_id = c.fetchone()
                    if location_id:
                        country = location_id[0]
                    else:
                        country = None

                if cluster:
                    c.execute(f"select id from rh_cluster where code='{cluster}'")
                    cluster_id = c.fetchone()
                    if cluster_id:
                        cluster = cluster_id[0]
                    else:
                        cluster = None

                domain.append(True)
                # m2m_records.append({'cluster': cluster, 'country': country})
                domain.pop(2)

                aquery = f"""insert into {table}(code, name, is_active) values (%s, %s, %s)
                """
                c.execute(aquery, domain)
                last_domain_id = c.lastrowid

                if last_domain_id and country:
                    coquery = f"""
                        insert into 
                        rh_activitydomain_countries(activitydomain_id, location_id) 
                        values({last_domain_id}, {country})
                    """
                    c.execute(coquery)
                if last_domain_id and cluster:
                    clquery = f"""
                           insert into 
                           rh_activitydomain_clusters(activitydomain_id, cluster_id) 
                           values({last_domain_id}, {cluster})
                       """
                    c.execute(clquery)

            c.execute("DROP TABLE tmp_activitydomain;")
        except Exception as exception:
            print(f"ERROR: import_activity_domain: {exception}")
            engine_connection.rollback()


def import_activity_descriptions_from_csv(conn, activity_description_csv):
    
    df = pd.read_csv(activity_description_csv)

    if len(df) > 0:
        table = "rh_activitytype"

        df.to_sql("tmp_activitytype", conn, if_exists="replace", index=False)

        try:
            c.execute(
                """select activity_description_id,activity_description_name,activity_type_id,cluster_id 
                from tmp_activitytype
            """
            )
            activity_types = c.fetchall()
            count = 0
            for activity_type in activity_types:
                activity_type = list(activity_type)
                activity_domain = activity_type[2] # activity_type_id
                cluster = activity_type[3] # cluster_id
                country = "AF"

                if activity_domain:
                    c.execute(
                        f"select id from rh_activitydomain where code='{activity_domain}'"
                    )
                    activity_domain_id = c.fetchone()
                    if activity_domain_id:
                        activity_domain = activity_domain_id[0]
                    else:
                        activity_domain = None

                if cluster:
                    c.execute(f"select id from rh_cluster where code='{cluster}'")
                    cluster_id = c.fetchone()
                    if cluster_id:
                        cluster = cluster_id[0]
                    else:
                        cluster = None

                if country:
                    c.execute(f"select id from rh_location where code='{country}'")
                    location_id = c.fetchone()
                    if location_id:
                        country = location_id[0]
                    else:
                        country = None

                activity_type.append(True)
                activity_type.pop(3)

                activity_type[2] = activity_domain
                activity_type.append(None)
                activity_type.append(None)
                activity_type.append(None)
                activity_type.append(None)
                activity_type.append(None)
                activity_type.append(None)
                activity_type.append(None)

                # activity_type[4] = indicator

                aquery = f"""insert into {table}(code,name,activity_domain_id,is_active,activity_date,
                hrp_code,code_indicator,start_date,end_date,ocha_code,objective_id) 
                    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                try:
                    c.execute(aquery, activity_type)
                except Exception as exception:
                    # print(f"EXEC: {exception}")
                    count = count + 1
                    continue
                
                last_activity_type_id = c.lastrowid

                if last_activity_type_id and country:
                    coquery = f"""
                        insert into 
                        rh_activitytype_countries(activitytype_id, location_id) 
                        values({last_activity_type_id}, {country})
                    """
                    c.execute(coquery)
                if last_activity_type_id and cluster:
                    clquery = f"""
                        insert into 
                        rh_activitytype_clusters(activitytype_id, cluster_id) 
                        values({last_activity_type_id}, {cluster})
                    """
                    c.execute(clquery)
                # if last_activity_type_id and indicator:
                #     inquery = f"""
                #         insert into
                #         rh_activitytype_indicators(activitytype_id, indicator_id)
                #         values({last_activity_type_id}, {indicator})
                #     """
                #     c.execute(inquery)
            if count > 0:
                print(f"Log: {count} activitytype was not inserted to the DB due to constraint error")
            c.execute("DROP TABLE tmp_activitytype;")
        except Exception as exception:
            print(f"ERROR: import_activity_description: {exception}")
            engine_connection.rollback()


def import_activity_details_from_csv(conn, activity_details_csv):
    """
    Import updated clusters from CSV
    """
    
    df = pd.read_csv(activity_details_csv)

    if len(df) > 0:
        table = "rh_activitydetail"

        df.to_sql("tmp_activitydetail", conn, if_exists="replace", index=False)

        try:
            c.execute(
                "select activity_description_id,activity_detail_id,activity_detail_name from tmp_activitydetail"
            )
            activity_details = c.fetchall()
            m2m_records = []
            count = 0
            for activity_detail in activity_details:
                activity_detail = list(activity_detail)
                activity_type = activity_detail[0]
                # country = 'AF'

                if activity_type:
                    c.execute(
                        f"select id from rh_activitytype where code='{activity_type}'"
                    )
                    activity_type_id = c.fetchone()
                    if activity_type_id:
                        activity_type = activity_type_id[0]
                    else:
                        activity_type = None

                activity_detail[0] = activity_type

                aquery = f"""insert into {table}(activity_type_id, code, name) values (%s, %s, %s)
                """

               

                try:
                    c.execute(aquery, activity_detail)
                except Exception as exception:
                    print(f"LOG: EXEC acitivity-details: {exception}")
                    count = count + 1
                    continue
            
            if count > 0:
                print(f"Log: {count} activitydetail was not inserted to the DB due to constraint error")

            c.execute("DROP TABLE tmp_activitydetail;")
        except Exception as exception:
            print(f"ERROR: import_activity_details_from_csv: {exception}")
            engine_connection.rollback()


def import_beneficiary_types_from_csv(conn, beneficiary_type_csv):
    """
    Import beneficiary types from CSV
    """
    
    df = pd.read_csv(beneficiary_type_csv)

    if len(df) > 0:
        table = "rh_beneficiarytype"

        df.to_sql("tmp_beneficiarytype", conn, if_exists="replace", index=False)

        try:
            c.execute(
                f"""
                    insert into 
                    {table}(name, code, description,is_active,type,country_id) 
                    select 
                    beneficiary_type_name, beneficiary_type_id, description,is_active,type,
                    (select id from rh_location where code = tmp_beneficiarytype.admin0pcode)
                    from tmp_beneficiarytype"""
            )

        except Exception as exception:
            print(f"Error b_type: {exception}")
            engine_connection.rollback()
            
        try:
            c.execute('SELECT id,code FROM rh_cluster')
            cluster_ids = c.fetchall()
            
            c.execute('SELECT cluster_code,beneficiary_type_id FROM tmp_beneficiarytype')
            beneficiary_ids = c.fetchall()

            for cluster_id in cluster_ids:
                for b_id in beneficiary_ids:
                    b_cluster_code = b_id[0]
                    cluster_code = cluster_id[1]
                    
                    if b_cluster_code == cluster_code:    
                        query = f"""
                        INSERT INTO rh_beneficiarytype_clusters (beneficiarytype_id, cluster_id)
                        VALUES ((select id from rh_beneficiarytype where code = '{b_id[1]}'),{cluster_id[0]})
                        """
                        c.execute(query)
                        
            c.execute("DROP TABLE tmp_beneficiarytype;")
        except Exception as e:
            print(f"Error in b_type and cluster: {e}")
            engine_connection.rollback()


def import_organizations_from_csv(conn, organizations_csv):
    """
    Import organizations from CSV
    """
    
    df = pd.DataFrame()
    df = pd.read_csv(organizations_csv)

    if len(df) > 0:
        table = "rh_organization"

        df.to_sql("tmp_organization", conn, if_exists="replace", index=False)
        try:
            c.execute(
                """select _id, "createdAt", organization, organization_name, organization_type, 
                "updatedAt", admin0pcode from tmp_organization"""
            )
            organizations = c.fetchall()
            for organization in organizations:
                organization = list(organization)
                country = organization.pop()
                organization = tuple(organization)
                oquery = f"""
                        insert into 
                        {table}(old_id, created_at, code, name, type, updated_at) 
                        values (%s, %s, %s, %s, %s, %s)
                    """
                c.execute(oquery, organization)
                last_org_id = c.lastrowid

                lquery = f"""select id from rh_location where code='{country}'"""
                c.execute(lquery)
                country_id = c.fetchone()

                if last_org_id and country_id:
                    olquery = f"""
                                insert into 
                                rh_organization_countries(organization_id, location_id) 
                                values({last_org_id}, {country_id[0]})
                            """
                    c.execute(olquery)
            c.execute("DROP TABLE tmp_organization;")
        except Exception as exception:
            print("exception: ", exception)
            engine_connection.rollback()


def import_donors_from_csv(conn, donors_csv):
    """
    Import Donors from CSV
    """
    
    df = pd.DataFrame()
    df = pd.read_csv(donors_csv)

    if len(df) > 0:
        table = "rh_donor"

        df.to_sql("tmp_donor", conn, if_exists="replace", index=False)

        try:
            c.execute(
                """select _id, end_date, project_donor_id, project_donor_name, start_date, 
                admin0pcode from tmp_donor"""
            )
            donors = c.fetchall()
            for donor in donors:
                donor = list(donor)
                country = donor.pop()
                if not donor[1]:
                    donor[1] = datetime.now()
                if not donor[-1]:
                    donor[-1] = datetime.now()

                donor = tuple(donor)
                dquery = f"""
                        insert into 
                        {table}(old_id, updated_at, code, name, created_at) 
                        values (%s, %s, %s, %s, %s)
                    """
                c.execute(dquery, donor)
                last_donor_id = c.lastrowid

                lquery = f"""select id from rh_location where code='{country}'"""
                c.execute(lquery)
                country_id = c.fetchone()

                if last_donor_id and country_id:
                    olquery = f"""
                                insert into 
                                rh_donor_countries(donor_id, location_id) 
                                values({last_donor_id}, {country_id[0]})
                            """
                    c.execute(olquery)
                # TODO: Add the clusters as well
            c.execute("DROP TABLE tmp_donor;")

        except Exception as exception:
            print(f"ERROR: donors: {exception}")
            engine_connection.rollback()


def import_users_from_csv(conn, users_csv):
    """
    Import Users from CSV
    """
    

    df = pd.DataFrame()
    df = pd.read_csv(users_csv)

    if len(df) > 0:
        table = "auth_user"

        df.to_sql("tmp_accounts", conn, if_exists="replace", index=False)

        try:
            c.execute(
                "select admin0pcode,cluster_id,organization_id,phone,position,skype,username from tmp_accounts"
            )
            profile_info = c.fetchall()
            c.execute(
                """select "createdAt",email,last_logged_in,password,status,username,name from tmp_accounts"""
            )
            users = c.fetchall()
            profiles_list = []
            for profile in profile_info:
                profile = list(profile)
                skype = profile[5]
                if not skype:
                    profile[5] = None
                country = profile[0]
                cluster = profile[1]
                organization = profile[2]
                if country:
                    c.execute(f"select id from rh_location where code='{country}'")
                    location_id = c.fetchone()
                    if location_id:
                        profile[0] = location_id[0]
                    else:
                        profile[0] = None

                if cluster:
                    if cluster in ["coordination", "smsd"]:
                        cluster = "cccm"
                    if cluster == "agriculture":
                        cluster = "fsac"
                    if cluster == "rnr_chapter":
                        cluster = "protection"
                    c.execute(
                        f"select id from rh_cluster where code='{cluster}' or title='{cluster}' or name='{cluster}'"
                    )
                    cluster_id = c.fetchone()
                    if cluster_id:
                        profile[1] = cluster_id[0]
                    else:
                        profile[1] = None

                if organization:
                    c.execute(
                        f"select id from rh_organization where old_id='{organization}'"
                    )
                    organization_id = c.fetchone()
                    if organization_id:
                        profile[2] = organization_id[0]
                    else:
                        profile[2] = None

                profile = tuple(profile)
                profiles_list.append(profile)

            for user in users:
                user = list(user)

                name = user[6].split(" ")
                # fix index 1 out or range
                if len(name) == 1:
                    name.append("")

                user[6]=name[0] # firsname
                user.append(name[1]) # lastname

                if user[4] == "active":
                    user[4] = True

                if not user[5]: # username
                    continue

                password = user[3]
                if password:
                    user[3] = "bcrypt$" + password

                # user = ['NULL' if a==None else a for a in user]
                user = tuple(user)
                aquery = f"""
                        insert into 
                        {table}(date_joined, email, last_login, password,is_active ,username, last_name, first_name,is_superuser,is_staff) 
                        values (%s, %s, %s, %s, %s, %s, %s, %s,False,False)
                    """
                
                c.execute(aquery, user)
                c.execute("SELECT lastval();")
                user_id = c.fetchone()[0]

                c.execute(f"select username from {table} where id={user_id}")
                db_user = c.fetchone()
                # print(user)
                # print(db_user)
                # print("marker")
                u_profile = next(item for item in profiles_list if db_user[0] in item)
                
                profile_cluster_id = False
                if u_profile:
                    u_profile = list(u_profile)
                    u_profile.pop(-1)
                    profile_cluster_id = u_profile.pop(1)
                    u_profile.append(user_id)
                    u_profile.append(False)
                    u_profile = tuple(u_profile)
                pquery = f"""
                        insert into 
                        users_profile(country_id,organization_id,phone,position,skype,user_id,is_cluster_contact) 
                        values (%s, %s, %s, %s, %s, %s, %s)
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
        except Exception as exception:
            print("***********IMPORT ERROR - USER ************ ", exception)
            engine_connection.rollback()


def import_facilities_from_csv(conn, facilities_csv):
    """
    Import Facility types from CSV
    """
    
    df = pd.read_csv(facilities_csv)

    if len(df) > 0:
        table = "rh_facilitysitetype"

        df.to_sql("tmp_facilitysitetype", conn, if_exists="replace", index=False)
        try:
            c.execute("select cluster,name from tmp_facilitysitetype")
            facility_site_types = c.fetchall()
            for site in facility_site_types:
                site = list(site)
                cluster = site[0]

                if cluster:
                    c.execute(f"select id from rh_cluster where code='{cluster}'")
                    cluster_id = c.fetchone()
                    if cluster_id:
                        cluster = cluster_id[0]
                    else:
                        cluster = None
                site[0] = cluster

                aquery = f"""insert into {table}(cluster_id, name) values (%s, %s)
                """
                c.execute(aquery, site)

            c.execute("DROP TABLE tmp_facilitysitetype;")
        except Exception as exception:
            print(f"ERROR: import_facilities_from_csv: {exception}")
            engine_connection.rollback()


def import_dissaggregation_from_csv(conn, diss_csv):
    """
    Import disaggregation types from CSV
    """
    
    df = pd.read_csv(diss_csv)

    if len(df) > 0:
        table = "rh_disaggregation"

        df.to_sql("tmp_diss", conn, if_exists="replace", index=False)

        try:
            c.execute(
                f"""
                    insert into 
                    {table}(name, gender, lower_limit, upper_limit,created_at,updated_at) 
                    select 
                    name,gender,lower_limit,upper_limit,now(),now()
                    from tmp_diss"""
            )
            c.execute("DROP TABLE tmp_diss;")
        except Exception as exception:
            print(f"Error in DISAG: {exception}")
            engine_connection.rollback()

        try:
            # Retrieve all IDs from the cluster table
            c.execute('SELECT id FROM rh_cluster')
            cluster_ids = c.fetchall()

            c.execute('SELECT id FROM rh_indicator')
            indicator_ids = c.fetchall()

            # Retrieve all IDs from the disaggregation table
            c.execute('SELECT id FROM rh_disaggregation')
            disaggregation_ids = c.fetchall()

            # Insert the IDs into the cluster_disaggregation table
            for cluster_id in cluster_ids:
                for disaggregation_id in disaggregation_ids:
                    c.execute('''
                    INSERT INTO rh_disaggregation_clusters (disaggregation_id, cluster_id)
                    VALUES (%s, %s)
                    ''', (disaggregation_id[0],cluster_id[0]))

            # Insert the IDs into the cluster_disaggregation table
            for indicator_id in indicator_ids:
                for disaggregation_id in disaggregation_ids:
                    c.execute('''
                    INSERT INTO rh_disaggregation_indicators (disaggregation_id, indicator_id)
                    VALUES (%s, %s)
                    ''', (disaggregation_id[0],indicator_id[0]))
        except Exception as e:
            print(f"Error in diss and cluster: {exception}")
            engine_connection.rollback()




# Try to import the data from different sources.
try:
    import_currencies_from_csv(connection, CURRENCIES_CSV)
    import_locations(connection, LOCATIONS_CSV)
    import_clusters_from_csv(connection, CLUSTERS)

    # Moved to load_acvtivities
    # import_activity_domains_from_csv(connection, ACTIVITY_DOMAIN_CSV) # Moved to load_acvtivities
    # import_activity_descriptions_from_csv(connection, ACTIVITY_DESCRIPTION_CSV) # Moved to load_acvtivities
    # import_activity_details_from_csv(connection, ACTIVITY_DETAIL_CSV) # Moved to load_acvtivities
    # import_indicators_from_csv(connection, INDICATORS_CSV) # Moved to load_acvtivities

    import_organizations_from_csv(connection, ORGANIZATIONS_CSV)

    import_donors_from_csv(connection, DONORS_CSV)

    import_users_from_csv(connection, USERS_CSV) # Moved to load_acvtivities

    import_facilities_from_csv(connection, FACILITIES)

    import_beneficiary_types_from_csv(connection,BENEFICIARY_TYPES_CSV)

    import_dissaggregation_from_csv(connection,DISS_CSV)

    import_stock_units_from_csv(connection, STOCKUNIT_CSV)

    import_stockitems_types_from(connection, STOCKITEMS_TYPES_CSV)
    
    engine_connection.commit()


except Exception as exc:
    print("***********IMPORT ERROR:************ ", exc)
    print("***********Traceback:************ ", traceback.format_exc())
    print("***********Roll Back The Commits************ ")
    engine_connection.rollback()

engine_connection.close()
