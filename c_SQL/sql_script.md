## mysql script


```sql

# firm id use consignee facset id for now
# country src_country
# product hs6
# yyyymm actual arrival date
# deals = numbs of transaction
# value = sum of all items
# weight = unit code as KG for now

# s.hts_code,
select 
entity2.entity_proper_name,
parent2.factset_ult_parent_entity_id as 'consignee_parent_factset_id',
entity3.entity_proper_name,
parent3.factset_ult_parent_entity_id as "shipper_parent_factset_id",
COUNT(s.transaction_id) as 'deals',
s.hts_code,
left(s.hts_code,6) as HS6,
SUM(s.hts_value) as "value", 
SUM(s.weight) as "weight/kg",
DATE_FORMAT(s.actual_arrival_date,'%Y%m')as yyyymm,
entity1.iso_country as 'src_country',
hts_map.hts_desc
#entity1.entity_proper_name as "company",

#sector.primary_sic_code,sector.industry_code,sector.sector_code,
#sec.fsym_id,
#cusip.cusip,
#isin.isin,
#sedol.sedol,
#region.ticker_region,
#exch.ticker_exchange

#into outfile "D:\\lc\\data_sample.csv" fields terminated by ',' LINES TERMINATED BY '\n'
from sample2017 s
join sym_v1_sym_entity entity1 on entity1.factset_entity_id = s.orig_port_factset_entity_id
join sym_v1_sym_entity shpentity on shpentity.factset_entity_id=s.shipper_factset_entity_id
join sc_v1_sc_ship_parent parent2 on parent2.factset_entity_id =s.consignee_factset_entity_id 
join sym_v1_sym_entity entity2 on entity2.factset_entity_id = parent2.factset_ult_parent_entity_id
join sc_v1_sc_ship_parent parent3 on parent3.factset_entity_id =s.shipper_factset_entity_id
join sym_v1_sym_entity entity3 on entity3.factset_entity_id = parent3.factset_ult_parent_entity_id
#join sc_v1_sc_ship_sec_entity sec on sec.factset_entity_id = parent2.factset_ult_parent_entity_id


#left join sym_v1_sym_entity_sector sector on sector.factset_entity_id =  parent.factset_ult_parent_entity_id
#left join sym_v1_sym_cusip cusip on cusip.fsym_id =  sec.fsym_id
#left join sym_v1_sym_isin isin on isin.fsym_id = sec.fsym_id
#left join sym_v1_sym_sedol sedol on left(sedol.fsym_id,6) = left(sec.fsym_id,6)
#left join sym_v1_sym_ticker_region region on left(region.fsym_id,6)= left(sec.fsym_id,6)
#left join sym_v1_sym_ticker_exchange exch on left(exch.fsym_id,6) =  left(sec.fsym_id,6)
left join ref_v2_hts_code_map hts_map on hts_map.hts_code=s.hts_code
group by parent2.factset_ult_parent_entity_id,parent3.factset_ult_parent_entity_id,s.hts_code,yyyymm
order by yyyymm
limit 100

```

## cnt_level_match_without_group

```sql
select 
"shp_proper_name",	"shpentity_country",	"shp_entity_type"	,"shipper_factset_entity_id",	"shp_compmany_id"	,"shp_sic_code"	,"shp_industry_code",	"shp_sector_code"	,"con_proper_name","conentity_country",	"con_entity_type"	,"consignee_factset_entity_id",	"con_compmany_id",	"con_sic_code"	,"con_industry_code",	"con_sector_code",	"carrier_factset_entity_id"	,"estimated_arrival_date",	"actual_arrival_date"	,"orig_port_factset_entity_id",	"dest_port_factset_entity_id",	"item_id",	"transaction_id"	,"container_id",	"manifest_qty"	,"manifest_unit_code",	"manifest_desc",	"hts_type"	,"hts_code"	,"hts_value",	"weight",	"weight_unit_code"	,"piece_count"
UNION ALL
select 

shpentity.entity_proper_name as shp_proper_name,
shpentity.iso_country as shpentity_country,
shpentity.entity_type as shp_entity_type,
trans.shipper_factset_entity_id,
shpparent.factset_ult_parent_entity_id as shp_compmany_id,
shpsector.primary_sic_code as shp_sic_code,
shpsector.industry_code as shp_industry_code,
shpsector.sector_code as shp_sector_code,
conentity.entity_proper_name as con_proper_name,
conentity.iso_country as conentity_country,
conentity.entity_type as con_entity_type,
trans.consignee_factset_entity_id,
conparent.factset_ult_parent_entity_id as con_compmany_id,
consector.primary_sic_code as con_sic_code,
consector.industry_code as con_industry_code,
consector.sector_code as con_sector_code,

trans.carrier_factset_entity_id,
trans.estimated_arrival_date ,
trans.actual_arrival_date,
trans.orig_port_factset_entity_id,
trans.dest_port_factset_entity_id,

cnt.item_id,
cnt.transaction_id,
cnt.container_id,
cnt.manifest_qty,
cnt.manifest_unit_code,
cnt.manifest_desc,
cnt.hts_type,
cnt.hts_code,
cnt.hts_value,
cnt.weight,
cnt.weight_unit_code,
cnt.piece_count







#into lc_cnt_expand in facset

from sc_v1_sc_ship_trans_cnt_curr cnt
left join sc_v1_sc_ship_trans_curr trans on trans.transaction_id = cnt.transaction_id
left join sc_v1_sc_ship_parent shpparent on shpparent.factset_entity_id=trans.shipper_factset_entity_id
left join sc_v1_sc_ship_parent conparent on  conparent.factset_entity_id=trans.consignee_factset_entity_id
left join sym_v1_sym_entity shpentity on shpentity.factset_entity_id=shpparent.factset_ult_parent_entity_id
left join sym_v1_sym_entity conentity on conentity.factset_entity_id=conparent.factset_ult_parent_entity_id

left join sym_v1_sym_entity_sector shpsector on shpsector.factset_entity_id=shpparent.factset_ult_parent_entity_id

left join sym_v1_sym_entity_sector consector on consector.factset_entity_id=conparent.factset_ult_parent_entity_id



limit 100


INTO OUTFILE 'F://lc//ship data//facset examples//cnt_data_all.csv'
FIELDS TERMINATED BY '|'
ENCLOSED BY '"'
LINES TERMINATED BY '\n';
```

## fsym_all

```sql
select 
"fsym_id",
"factset_entity_id",
"isin",
"sedol",
"cusip",
"currency",
"proper_name",
"regional_flag",
"security_flag",
"fsym_regional_id",
"fsym_security_id"

UNION ALL

select 
fsym.fsym_id,
fsym.factset_entity_id,
isin.isin,
sedol.sedol,
cusip.cusip,
coverage.currency,
coverage.proper_name,
coverage.regional_flag,
coverage.security_flag,
coverage.fsym_regional_id,
coverage.fsym_security_id 
from 
sc_v1_sc_ship_sec_entity fsym
left join sym_v1_sym_isin isin on isin.fsym_id=fsym.fsym_id
left join sym_v1_sym_sedol sedol on sedol.fsym_id=fsym.fsym_id
left join sym_v1_sym_cusip cusip on cusip.fsym_id=fsym.fsym_id
left join sym_v1_sym_coverage coverrage on coverage.fsym_id=fsym.fsym_id
limit 100

INTO OUTFILE 'F://lc//ship data//facset examples//fsym_data_all.csv'
FIELDS TERMINATED BY '|'
ENCLOSED BY '"'
LINES TERMINATED BY '\n';
```

## cnt_new

```sql
create table cnt_trans_data as
select 

shpentity.entity_proper_name as shp_ult_proper_name,
shpentity.iso_country as shpentity_country,
shpentity.entity_type as shp_entity_type,
trans.shipper_factset_entity_id,
shipperentity.entity_proper_name as shipper_name ,
shpparent.factset_ult_parent_entity_id as shp_compmany_id,

conentity.entity_proper_name as con_ult_proper_name,
conentity.iso_country as conentity_country,
conentity.entity_type as con_entity_type,
trans.consignee_factset_entity_id,
consigneeentity.entity_proper_name as consignee_name ,
conparent.factset_ult_parent_entity_id as con_compmany_id,

trans.carrier_factset_entity_id,
trans.actual_arrival_date,
trans.orig_port_factset_entity_id,
origentity.entity_proper_name as orig_port_name,
origentity.iso_country as orig_country,
trans.dest_port_factset_entity_id,
destentity.entity_proper_name as dest_port_name,
destentity.iso_country as dest_country,

cnt.item_id,
cnt.transaction_id,
cnt.container_id,
cnt.manifest_qty,
cnt.manifest_unit_code,
cnt.hts_code,
cnt.hts_value,
cnt.weight,
cnt.weight_unit_code,
cnt.piece_count


from sc_v1_sc_ship_trans_cnt_curr cnt
left join sc_v1_sc_ship_trans_curr trans on trans.transaction_id = cnt.transaction_id
left join sc_v1_sc_ship_parent shpparent on shpparent.factset_entity_id=trans.shipper_factset_entity_id
left join sc_v1_sc_ship_parent conparent on  conparent.factset_entity_id=trans.consignee_factset_entity_id
left join sym_v1_sym_entity shpentity on shpentity.factset_entity_id=shpparent.factset_ult_parent_entity_id
left join sym_v1_sym_entity conentity on conentity.factset_entity_id=conparent.factset_ult_parent_entity_id
left join sym_v1_sym_entity_sector shpsector on shpsector.factset_entity_id=shpparent.factset_ult_parent_entity_id
left join sym_v1_sym_entity_sector consector on consector.factset_entity_id=conparent.factset_ult_parent_entity_id
left join sym_v1_sym_entity shipperentity on shipperentity.factset_entity_id=trans.shipper_factset_entity_id
left join sym_v1_sym_entity consigneeentity on consigneeentity.factset_entity_id=trans.consignee_factset_entity_id
left join sym_v1_sym_entity origentity on origentity.factset_entity_id=trans.orig_port_factset_entity_id
left join sym_v1_sym_entity destentity on destentity.factset_entity_id=trans.dest_port_factset_entity_id


where "2018-01-01"<=trans.actual_arrival_date

limit 100
```

