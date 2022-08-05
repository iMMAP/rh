import sqlite3
import pandas as pd


con = sqlite3.connect("../db.sqlite3")


df = pd.read_csv('../data/af_loc.csv')

df['Long'] = df['Long'].str.replace(',', '.').astype(float)
df['Lat'] = df['Lat'].str.replace(',', '.').astype(float)

df.to_sql('tmp_locs', con, index=False)

con.execute("""
insert into rh_location (level, parent_id, code, name, original_name, type, created_at, updated_at)
select distinct 0 level, 0 parent, ADM0_PCODE code, ADM0_NA_EN name, ADM0_translation original_name, 'country' type, datetime('now') created_at, datetime('now') updated_at from tmp_locs
""")

con.execute("""
insert into rh_location (level, parent_id, code, name, original_name, type, created_at, updated_at)
select distinct 1 level, r.id as parent_id, ADM1_PCODE code, ADM1_NA_EN name, ADM1_translation original_name, 'province' type, datetime('now') created_at, datetime('now') updated_at
from tmp_locs t inner join rh_location r ON r.code = t.ADM0_PCODE;
""")

con.execute("""
insert into rh_location (level, parent_id, code, name, type, lat, long, created_at, updated_at)
select distinct 2 level, r.id as parent_id, ADM2_PCODE code, ADM2_NA_EN name, 'district' type, t.lat, t.long, datetime('now') created_at, datetime('now') updated_at
from tmp_locs t inner join rh_location r ON r.code = t.ADM1_PCODE;
""")
