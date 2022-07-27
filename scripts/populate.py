import sqlite3
import pandas as pd


con = sqlite3.connect("../db.sqlite3")

ac = pd.read_csv(
    '../data/activities.csv', parse_dates=['start_date', 'end_date']
).drop_duplicates().dropna(
    subset=['activity_type_name']
).reset_index(drop=True)

ac.to_sql('tmp_activities', con, index=False)

con.execute("""
insert into rh_cluster (title) select distinct cluster from tmp_activities;
""")

con.execute("""
insert into rh_activity (cluster_id,title,start_date,end_date) select distinct id,activity_type_name,start_date,end_date 
from rh_cluster c inner join tmp_activities a on a."cluster"=c.title;
""")

con.execute("""
insert into rh_indicator (activity_id, title) select distinct ra.id, indicator_name from rh_activity ra inner join tmp_activities a where a.activity_type_name=ra.title and a.indicator_name not null;
""")

con.execute("DROP TABLE tmp_activities")

con.commit()