# 常用 postgreSQL 命令

```sql
-- 查看所有包含 usimport 的表格
select * from pg_tables where tablename like '%usimport%';


-- 查看所有的column_name
select column_name from information_schema.columns 
where table_name='panjivausimport2014';

-- 保存到本地 csv 文件

COPY (
  SELECT name, category_name
  FROM products
  LEFT JOIN categories ON categories.id = products.category_id
)
TO '/path/to/output.csv'
WITH csv;
```

