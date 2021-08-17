## 整合import

```sql


select 
distinct
imp2008.panjivarecordid,
imp2008.arrivaldate,
imp2008.conname,
imp2008.concity,
imp2008.constateregion,
imp2008.concountry,
imp2008.conpanjivaid,
imp2008.shpname,
imp2008.shpcity,
imp2008.shpstateregion,
imp2008.shpcountry,
imp2008.shppanjivaid,
imp2008.carrier,
imp2008.billofladingtype,
imp2008.shpmtorigin,
imp2008.shpmtdestination,
imp2008.shpmtdestinationregion,
imp2008.portoflading,
imp2008.portofladingregion,
imp2008.portofladingcountry,
imp2008.placeofreceipt,
imp2008.transportmethod,
imp2008.vessel,
imp2008.vesselvoyageid,
imp2008.vesselimo,
imp2008.volumeteu,
cast (substring(imp2008.quantity FROM '[0-9]+') as integer) as quantity_num,
cast (substring(imp2008.quantity FROM '[A-z]+') as varchar(8))as unit,
imp2008.weightkg,
imp2008.valueofgoodsusd,
imp2008.numberofcontainers,
-- imp2008.
cast (concross.identifierValue as integer) as conidentifierValue,
cast (shpcross.identifierValue as integer) as shpidentifierValue,
concross.companyid as conccrcompanyid,
shpcross.companyid as shpccrcompanyid,
concomp.companyid as conciqcompanyid,
shpcomp.companyid as shpciqcompanyid,
concomp.companyname as conciqcompanyname,
shpcomp.companyname as shpciqcompanyname,

shpultcomp.companyid as shpultcompanyid,
shpultcomp.companyname as shpultcompanyname,
conultcomp.companyid as conultcompanyid,
conultcomp.companyname as conultcompanyname,
replace(unnest(string_to_array(replace(replace(hs2008.hscode,'.',''),'Classified:',''), ';')),' ','') as hscode
-- REPLACE(left(hs2008.hsCode, 7), '.', '') as hscode6,
-- hsc.hscodedescription

into lcusimport2008
from panjivausimport2008 imp2008
left join panjivaCompanyCrossRef concross on cast (concross.identifierValue as integer)=imp2008.conpanjivaid
left join panjivaCompanyCrossRef shpcross on cast (shpcross.identifierValue as integer)=imp2008.shppanjivaid
left join ciqcompany concomp on concross.companyid=concomp.companyid
left join ciqcompany shpcomp on shpcross.companyid=shpcomp.companyid
left join panjivausimphscode2008 hs2008 on hs2008.panjivarecordid=imp2008.panjivarecordid

left join ciqCompanyUltimateParent shpparent on shpparent.companyid=shpcomp.companyid
left join ciqcompany shpultcomp on shpultcomp.companyid=shpparent.ultimateParentCompanyId
left join ciqCompanyUltimateParent conparent on conparent.companyid=concomp.companyid
left join ciqcompany conultcomp on conultcomp.companyid=conparent.ultimateParentCompanyId
;

```



## 整合export

```sql

select 
distinct
exp2019.panjivarecordid,
exp2019.shpmtdate,

exp2019.shpname,
exp2019.shpcity,
exp2019.shpstateregion,
exp2019.shpcountry,
exp2019.shppanjivaid,
exp2019.carrier,
exp2019.shpmtdestination,
exp2019.portoflading,
exp2019.portofladingregion,
exp2019.portofladingcountry,
exp2019.portofunlading,
exp2019.portofunladingregion,
exp2019.portofunladingcountry,
exp2019.placeofreceipt,
exp2019.vessel,
exp2019.vesselcountry,
exp2019.volumeteu,
cast (substring(exp2019.itemQuantity FROM '[0-9]+') as integer) as quantity_num,
cast (substring(exp2019.itemQuantity FROM '[A-z]+') as varchar(8))as unit,
exp2019.weightkg,
exp2019.valueofgoodsusd,
cast (shpcross.identifierValue as integer) as shpidentifierValue,
shpcross.companyid as shpccrcompanyid,
shpcomp.companyid as shpciqcompanyid,
shpcomp.companyname as shpciqcompanyname,
ultcomp.companyname as ultcompanyname,
ultcomp.companyid as ultcompanyid,
replace(unnest(string_to_array(replace(replace(hs2019.hscode,'.',''),'Classified:',''), ',')),' ','') as hscode

into lcusexport2019
from panjivausexport2019 exp2019

left join panjivaCompanyCrossRef shpcross on cast (shpcross.identifierValue as integer)=exp2019.shppanjivaid
left join ciqcompany shpcomp on shpcross.companyid=shpcomp.companyid
left join ciqCompanyUltimateParent parent on parent.companyid=shpcomp.companyid
left join ciqcompany ultcomp on ultcomp.companyid=parent.ultimateParentCompanyId
left join panjivausexphscode2019 hs2019 on hs2019.panjivarecordid=exp2019.panjivarecordid

-- left join panjivahsclassification hsc on hsc.hsCode = hscode
-- limit 100
```





##  imp按月分


```sql
select 

count(imp2016.panjivarecordid) as deals,
date_part('month', imp2016.arrivaldate::date) AS month,
imp2016.conname,
imp2016.concountry,
imp2016.conpanjivaid,
imp2016.shpname,
imp2016.shpcountry,
imp2016.shppanjivaid,
imp2016.transportmethod,
sum(imp2016.volumeteu) as volume,
sum(imp2016.quantity_num) as quantity_num,
imp2016.unit,
sum(imp2016.weightkg) as total_weight,
sum(imp2016.valueofgoodsusd) as total_value,
imp2016.conciqcompanyid,
imp2016.shpciqcompanyid,
imp2016.conciqcompanyname,
imp2016.shpciqcompanyname,
imp2016.hscode,
imp2016.conultcompanyid,
imp2016.shpultcompanyid,
imp2016.conultcompanyname,
imp2016.shpultcompanyname

from lcusimport2016 imp2016

group by 
month,
imp2016.conname,
imp2016.concountry,
imp2016.conpanjivaid,
imp2016.shpname,
imp2016.shpcountry,
imp2016.shppanjivaid,
imp2016.transportmethod,
imp2016.unit,
imp2016.conciqcompanyid,
imp2016.shpciqcompanyid,
imp2016.conciqcompanyname,
imp2016.shpciqcompanyname,

imp2016.conultcompanyid,
imp2016.shpultcompanyid,
imp2016.conultcompanyname,
imp2016.shpultcompanyname,
imp2016.hscode
```



## exp按月分


```sql
select 

count(exp2019.panjivarecordid) as deals,
date_part('month', exp2019.shpmtdate::date) AS shp_month,
exp2019.shpname,
exp2019.shpcountry,
exp2019.shppanjivaid,
sum(exp2019.volumeteu) as volume,
sum(exp2019.quantity_num) as quantity_num,
exp2019.unit,
sum(exp2019.weightkg) as total_weight,
sum(exp2019.valueofgoodsusd) as total_value,
exp2019.shpciqcompanyid,
exp2019.shpciqcompanyname,
exp2019.hscode,
exp2019.ultcompanyid,
exp2019.ultcompanyname,
exp2019.shpmtdestination,
exp2019.portofladingcountry,
exp2019.portofunladingcountry

from lcusexport2019 exp2019

group by 
shp_month,
exp2019.shpname,
exp2019.shpcountry,
exp2019.shppanjivaid,
exp2019.unit,
exp2019.shpciqcompanyid,
exp2019.shpciqcompanyname,

exp2019.ultcompanyid,
exp2019.ultcompanyname,
exp2019.hscode,
exp2019.shpmtdestination,
exp2019.portofladingcountry,
exp2019.portofunladingcountry
```



## add new columns



```sql
错误
INSERT INTO lcusimport2016example
(conultcompanyid,shpultcompanyid,conultcompanyname,shpultcompanyname)
select 
conparent.ultimateparentcompanyid,
shpparent.ultimateparentcompanyid,
conultparent.companyname,
shpultparent.companyname



from lcusimport2016example imp2016
left join ciqCompanyUltimateParent shpparent on shpparent.companyid=imp2016.shpciqcompanyid
left join ciqCompanyUltimateParent conparent on conparent.companyid=imp2016.conciqcompanyid
left join ciqcompany conultparent on conultparent.companyid = conparent.ultimateparentcompanyid
left join ciqcompany shpultparent on shpultparent.companyid = shpparent.ultimateparentcompanyid

```

```sql
正确
ALTER TABLE tmptest
ADD COLUMN conultcompanyid VARCHAR,
ADD COLUMN shpultcompanyid VARCHAR,
ADD COLUMN conultcompanyname VARCHAR,
ADD COLUMN shpultcompanyname VARCHAR;
update tmptest
set shpultcompanyid = ultcompany.parentid,shpultcompanyname=ultcompany.companyname
from (
    select 
comp.companyid as companyid,
parent.companyid as parentid,
ultcomp.companyname as companyname
from ciqcompany comp
left join ciqCompanyUltimateParent parent on parent.companyid=comp.companyid
left join ciqcompany ultcomp on ultcomp.companyid=parent.companyid
--left join ciqCompanyUltimateParent conparent on conparent.companyid=imp2016.conciqcompanyid
--left join ciqcompany conultparent on conultparent.companyid = conparent.ultimateparentcompanyid
--left join ciqcompany shpultparent on shpultparent.companyid = shpparent.ultimateparentcompanyid

)ultcompany
where ultcompany.companyid=tmptest.shpccrcompanyid ;

update tmptest
set conultcompanyid = ultcompany.parentid,conultcompanyname=ultcompany.companyname
from (
    select 
comp.companyid as companyid,
parent.companyid as parentid,
ultcomp.companyname as companyname
from ciqcompany comp
left join ciqCompanyUltimateParent parent on parent.companyid=comp.companyid
left join ciqcompany ultcomp on ultcomp.companyid=parent.companyid
--left join ciqCompanyUltimateParent conparent on conparent.companyid=imp2016.conciqcompanyid
--left join ciqcompany conultparent on conultparent.companyid = conparent.ultimateparentcompanyid
--left join ciqcompany shpultparent on shpultparent.companyid = shpparent.ultimateparentcompanyid

)ultcompany
where ultcompany.companyid=tmptest.conccrcompanyid ;
```

## load to file

```sql
copy(select * from table)
TO 'F:\lc\panjiva\data\usimport2020monthly.csv' DELIMITER ',' CSV HEADER 
```

## update 

```sql
update lcusimport2019 imp2019
set imp2019.hscode = replace(imp2019.hscode,'Classified:','')
```

上面这个只跑了一个2019，还需要跑别的所有年份

##  public firm comparison

目标，统计不同尺度下的上市公司数目

Panjiva中public firm和deal使用和不使用ultimate parent-subsidary match table有多少区别（conciq, shpciq, conciq_public, conciq_public, conciq_matchedpublic, conciq_matchedpublic, deal, deal_public, deal_matchedpublic)？

```sql
select 



from lcusimport2016
```

## 2021-6-17 Shiyilin Xuqiu 

思路：

因为之前lcimport已经整理了大部分内容出来，所以先从lcimport中导出

```sql
```

主要是缺gvkey，找一下之前做cross的时候用的什么内容