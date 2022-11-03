-- org table 
CREATE TABLE org (id INTEGER PRIMARY KEY AUTOINCREMENT, name, short, type);

INSERT INTO org (name,short,type)
SELECT name,short,type FROM tmp_org;
---------------------


-- project table 
CREATE TABLE project (id INTEGER PRIMARY KEY AUTOINCREMENT, _id, country, cluster, org_id, title, description, budget, start_date, end_date, created_at, updated_at);

INSERT INTO project (_id, country, cluster, org_id, title, description, budget, start_date, end_date, created_at, updated_at)
SELECT p._id, p.country, p.cluster, o.id, p.title, p.description, p.budget, p.start_date, p.end_date, p.created_at, p.updated_at FROM 
tmp_project p INNER JOIN org o ON p.org_name=o.name and p.org_short=o.short;

---------------------

-- report table 
CREATE TABLE report (id INTEGER PRIMARY KEY AUTOINCREMENT, _id, project_id, month, year, status, active, submitted_at, created_at, updated_at);

INSERT INTO report (_id, project_id, month, year, status, active, submitted_at, created_at, updated_at)
SELECT r._id, p.id, r.month, r.year, r.status, r.active, r.submitted_at, r.created_at, r.updated_at FROM 
tmp_report r INNER JOIN project p ON p._id=r.project__id;
-----------------------

-- benef category 
CREATE TABLE benef_category (id INTEGER PRIMARY KEY AUTOINCREMENT,name);

INSERT INTO benef_category (name)
SELECT DISTINCT benef_category FROM tmp_target_benef WHERE benef_category iS NOT NULL;
--------------------------

-- benef type
CREATE TABLE benef_type (id INTEGER PRIMARY KEY AUTOINCREMENT,name);

INSERT INTO benef_type (name)
SELECT DISTINCT benef_type FROM tmp_benef WHERE benef_type iS NOT NULL;
--------------------------

-- hrp benef type
CREATE TABLE hrp_benef_type (id INTEGER PRIMARY KEY AUTOINCREMENT,name);

INSERT INTO hrp_benef_type (name)
SELECT DISTINCT hrp_benef_type FROM tmp_benef WHERE hrp_benef_type iS NOT NULL;
--------------------------

-- transfer category
CREATE TABLE transfer_category (id INTEGER PRIMARY KEY AUTOINCREMENT,name);

INSERT INTO transfer_category (name)
SELECT DISTINCT transfer_category FROM tmp_benef WHERE transfer_category iS NOT NULL;
--------------------------

-- grant type
CREATE TABLE grant_type (id INTEGER PRIMARY KEY AUTOINCREMENT,name);

INSERT INTO grant_type (name)
SELECT DISTINCT grant_type FROM tmp_benef WHERE grant_type iS NOT NULL;
--------------------------

-- delivery type
CREATE TABLE delivery_type (id INTEGER PRIMARY KEY AUTOINCREMENT,name);

INSERT INTO delivery_type (name)
SELECT DISTINCT delivery_type FROM tmp_benef WHERE delivery_type iS NOT NULL;
--------------------------

-- mpc delivery type
CREATE TABLE mpc_delivery_type (id INTEGER PRIMARY KEY AUTOINCREMENT,name);

INSERT INTO mpc_delivery_type (name)
SELECT DISTINCT mpc_delivery_type FROM tmp_benef WHERE mpc_delivery_type iS NOT NULL;
--------------------------

-- mpc mecanism type
CREATE TABLE mpc_mechanism_type (id INTEGER PRIMARY KEY AUTOINCREMENT,name);

INSERT INTO mpc_mechanism_type (name)
SELECT DISTINCT mpc_mechanism_type FROM tmp_benef WHERE mpc_mechanism_type iS NOT NULL;
--------------------------

-- package type
CREATE TABLE package_type (id INTEGER PRIMARY KEY AUTOINCREMENT,name);

INSERT INTO package_type (name)
SELECT DISTINCT package_type FROM tmp_benef WHERE package_type iS NOT NULL;
--------------------------

-- unit type
CREATE TABLE unit_type (id INTEGER PRIMARY KEY AUTOINCREMENT,name);

INSERT INTO unit_type (name)
SELECT DISTINCT unit_type FROM tmp_benef WHERE unit_type iS NOT NULL;
--------------------------

-- response type
CREATE TABLE response (id INTEGER PRIMARY KEY AUTOINCREMENT,name);

INSERT INTO response (name)
SELECT DISTINCT response FROM tmp_benef WHERE response iS NOT NULL;
--------------------------

CREATE TABLE activity (id INTEGER PRIMARY KEY AUTOINCREMENT,activity_type,activity_desc,activity_detail,indicator);

INSERT INTO activity (activity_type,activity_desc,activity_detail,indicator)
SELECT DISTINCT activity_type, activity_desc, activity_detail, indicator FROM (
SELECT DISTINCT activity_type, activity_desc, activity_detail, indicator from tmp_benef
UNION
SELECT DISTINCT activity_type, activity_desc, activity_detail, indicator from tmp_target_benef
);

-- SELECT DISTINCT activity_type, activity_desc, activity_detail, indicator FROM tmp_target_benef;

CREATE TABLE target_benef (id INTEGER PRIMARY KEY AUTOINCREMENT, project_id, activity_id, activity_type, activity_desc, activity_detail, benef_category_id, benef_category, indicator, boys, girls, men, women, households, elderly_men, elderly_women, total_pwd, created_at, updated_at);

INSERT INTO target_benef (project_id, activity_id, activity_type, activity_desc, activity_detail, benef_category_id, benef_category, indicator, boys, girls, men, women, households, elderly_men, elderly_women, total_pwd, created_at, updated_at)
SELECT p.id,a.id,tt.activity_type, tt.activity_desc, tt.activity_detail, bc.id, tt.benef_category, tt.indicator, tt.boys, tt.girls, tt.men, tt.women, tt.households, tt.elderly_men, tt.elderly_women, tt.total_pwd, tt.created_at, tt.updated_at FROM 
tmp_target_benef tt 
INNER JOIN project p ON p._id=tt.project__id
INNER JOIN activity a ON
a.activity_type=tt.activity_type AND
(a.activity_desc=tt.activity_desc OR (a.activity_desc IS NULL AND tt.activity_desc IS NULL)) AND 
(a.activity_detail=tt.activity_detail OR (a.activity_detail IS NULL AND tt.activity_detail IS NULL)) AND 
(a.indicator=tt.indicator OR (a.indicator IS NULL AND tt.indicator IS NULL))
LEFT JOIN benef_category bc ON bc.name=tt.benef_category
;


CREATE TABLE benef (id INTEGER PRIMARY KEY AUTOINCREMENT,report_id,activity_id,activity_type,activity_desc,activity_detail,benef_category,benef_category_id,benef_type,benef_type_id,hrp_benef_type,hrp_benef_type_id,transfer_category,transfer_category_id,grant_type,grant_type_id,delivery_type,delivery_type_id,mpc_delivery_type,mpc_delivery_type_id,mpc_mechanism_type,mpc_mechanism_type_id,package_type,package_type_id,unit_type,unit_type_id,indicator,response,response_id,boys,girls,men,women,households,elderly_men,elderly_women,total_pwd,loc_id,admin0name,adminRpcode,admin1pcode,admin1name,admin2pcode,admin2name,site_type,site_name,created_at,updated_at);

INSERT INTO benef (report_id,activity_id,activity_type,activity_desc,activity_detail,benef_category,benef_category_id,benef_type,benef_type_id,hrp_benef_type,hrp_benef_type_id,transfer_category,transfer_category_id,grant_type,grant_type_id,delivery_type,delivery_type_id,mpc_delivery_type,mpc_delivery_type_id,mpc_mechanism_type,mpc_mechanism_type_id,package_type,package_type_id,unit_type,unit_type_id,indicator,response,response_id,boys,girls,men,women,households,elderly_men,elderly_women,total_pwd,loc_id,admin0name,adminRpcode,admin1pcode,admin1name,admin2pcode,admin2name,site_type,site_name,created_at,updated_at)
SELECT r.id, a.id, tb.activity_type,tb.activity_desc,tb.activity_detail,tb.benef_category,bc.id,tb.benef_type,bt.id,tb.hrp_benef_type,hbt.id,tb.transfer_category,tc.id,tb.grant_type,gt.id,tb.delivery_type,dt.id,tb.mpc_delivery_type,mdt.id,tb.mpc_mechanism_type,mmt.id,tb.package_type,pt.id,tb.unit_type,ut.id,tb.indicator,tb.response,res.id,tb.boys,tb.girls,tb.men,tb.women,tb.households,tb.elderly_men,tb.elderly_women,tb.total_pwd,loc.id,tb.admin0name,tb.adminRpcode,tb.admin1pcode,tb.admin1name,tb.admin2pcode,tb.admin2name,tb.site_type,tb.site_name,tb.created_at,tb.updated_at
FROM 
tmp_benef tb 
INNER JOIN report r on r._id = tb.report__id
INNER JOIN activity a ON
a.activity_type=tb.activity_type AND
(a.activity_desc=tb.activity_desc OR (a.activity_desc IS NULL AND tb.activity_desc IS NULL)) AND 
(a.activity_detail=tb.activity_detail OR (a.activity_detail IS NULL AND tb.activity_detail IS NULL)) AND 
(a.indicator=tb.indicator OR (a.indicator IS NULL AND tb.indicator IS NULL))
LEFT JOIN benef_category bc ON bc.name = tb.benef_category
LEFT JOIN benef_type bt ON bt.name = tb.benef_type
LEFT JOIN hrp_benef_type hbt ON hbt.name = tb.hrp_benef_type
LEFT JOIN transfer_category tc ON tc.name = tb.transfer_category
LEFT JOIN grant_type gt ON gt.name = tb.grant_type
LEFT JOIN delivery_type dt ON dt.name = tb.delivery_type
LEFT JOIN mpc_delivery_type mdt ON mdt.name = tb.mpc_delivery_type
LEFT JOIN mpc_mechanism_type mmt ON mmt.name = tb.mpc_mechanism_type
LEFT JOIN package_type pt ON pt.name = tb.package_type
LEFT JOIN unit_type ut ON ut.name = tb.unit_type
LEFT JOIN response res ON res.name = tb.response
LEFT JOIN locs loc ON loc.code = UPPER(tb.admin2pcode)
--INNER JOIN benef_category bc ON (bc.name = tb.benef_category OR (bc.name IS NULL AND tb.benef_category IS NULL))
;




ALTER TABLE project DROP COLUMN _id;
ALTER TABLE report DROP COLUMN _id;

ALTER TABLE target_benef DROP COLUMN benef_category;
ALTER TABLE benef DROP COLUMN benef_category;

ALTER TABLE benef DROP COLUMN benef_type;
ALTER TABLE benef DROP COLUMN hrp_benef_type;
ALTER TABLE benef DROP COLUMN transfer_category;
ALTER TABLE benef DROP COLUMN grant_type;
ALTER TABLE benef DROP COLUMN delivery_type;
ALTER TABLE benef DROP COLUMN mpc_delivery_type;
ALTER TABLE benef DROP COLUMN mpc_mechanism_type;
ALTER TABLE benef DROP COLUMN unit_type;
ALTER TABLE benef DROP COLUMN package_type;
ALTER TABLE benef DROP COLUMN response;
ALTER TABLE benef DROP COLUMN adminRpcode;
ALTER TABLE benef DROP COLUMN admin1pcode;
ALTER TABLE benef DROP COLUMN admin1name;
ALTER TABLE benef DROP COLUMN admin2pcode;
ALTER TABLE benef DROP COLUMN admin2name;
ALTER TABLE benef DROP COLUMN admin0name;
ALTER TABLE benef DROP COLUMN site_name;
ALTER TABLE benef DROP COLUMN site_type;



