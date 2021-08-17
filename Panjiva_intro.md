# Panjiva_intro

## GSS Measures

### 1.GL Global Sourcing Level (GL)
$$ GL_{it} = 100 \cdot \frac{\sum_{j=1}^{NS_t} ST_j \cdot IV_{itj}}{\sum_{j=1}^{NS}ST_j} \cdot \frac{1}{COGS_{it}}$$

#### Attribute
* $NS_t$ is the total number of distinct supplier countries from which firm i has imported goods in year t, 【t 年 i 公司从多少个国家直接进口】【Panjiva】

* $ST_j$ is the average shipment time from the jth supplier country to US,【j 国家运到美国花了的平均 ship time】【使用替代数据】

* $IV_{itj}$ is the total value of goods imported by firm i from the supplier country j【t 年 i 公司进口 j 国家 的年进口额】【Panjiva】

* $COGS_{it}$ is the corresponding year’s cost of goods sold.【t 年 i 公司的销售成本】【From WRDS】

#### Question
 
 * $ST_j$ 使用了网上的替代数据，没有使用来自【DBData】计算出的真实数据，可能会有较大的偏差
 
 * 替代数据来自 （https://www.searates.com/services/distances-time/）
***

### 2.Supplier Concentration (SC)
$$H\_Index_{itc} = \sum_{j=1}^{NS_{itc}}(\frac {IV_{itcj}}{IV_{itc}})^2$$
$$SC_{it}=\frac{\sum_{c=1}^{NC_{it}}IV_{itc} \cdot H\_Index_{itc}}{\sum_{c=1}^{NC_{it}}IV_{itc}}$$

#### Attribute
* $NS_{itc}$ is the total number of suppliers from whom product category c is sourced by firm i in year t 【t 年 i 公司在货物 c 上有多少个供应商】【Panjiva】

* $IV_{itcj}$ is the total value of imports by firm i from supplier j in category c【t 年 i 公司在货物 c 上从 j 供应商的进口总额】【Panjiva】

* $IV_{itc}$ is the total value of imports under product category c【t 年 i 公司在 c 货物上的进口总额】【Panjiva】

* $NC_{it}$ is the total number of product categories imported by firm i in year t.【t 年 i 公司进口了多少中货物】【Panjiva】

#### Question
* 在使用六位编码的 `hscode` 进行分类的时候，出现大量一家公司只有一家供应商的的情况

* SC 变量为 1 的值大约占据了 90%，在删去 compustat 里缺失值之后，SC 变量全部是 1，失去统计意义

* 将按照六位 hscode 编码进行修改，改为按照两位 hscode 进行分类
***

### 3.Sourcing Shipment Lead Time (LT)
$$SL_{itc} = \frac{\sum_{j=1}^{NSC_{itc}}IV_{itcj} \cdot Shipment\ Lead\ Time_{jt}}{\sum_{j=1}^{NSC_{itc}}IV_{itcj}}$$

$$SL_{it}  = \frac{\sum_{c=1}^{NC_{it}}IV_{itc} \cdot SL_{itc}}{\sum_{c=1}^{NC_{it}}IV_{itc}}$$

#### Attribute
* $NSC_{itc}$ is the number of supplier countries from which firm i imported category c in year t,【t 年 i 公司进口 c 商品来自几个国家】【Panjiva】

* Shipment Lead Time jt denotes the average shipment time between the supplier country j and US in year t. 【美国和 j 国家的平均shipping time】【From DBData】

#### Question
* lead time data 来自 DBData 数据库。DBData 是海关的清关数据，不是很能看得懂。

***

### 4.Logical Efficient in Sourcing (LE)

$$LE_{itc} = \frac{\sum_{j=1}^{NSC_{itc}}IV_{itcj} \cdot LPI_{jt}}{\sum_{j=1}^{NSC_{itc}}IV_{itcj}}$$

$$LE_{it}  = \frac{\sum_{c=1}^{NC_{it}}IV_{itc} \cdot LE_{itc}}{\sum_{c=1}^{NSC_{itc}}IV_{itc}}$$

#### Attribute
* $NSC_{itc}$ is the number of supplier countries from which firm i imported category c in year t,【t 年 i 公司进口 c 商品来自几个国家】【Panjiva】

* $IV_{itcj}$ is the total import value of category c goods from the supplier country j, 【t 年 i 公司进口 c 商品来自 j 国家的价值总额】【Panjiva】

* $LPI_{jt}$ is the performance score value for location j in year t.
【Word Bank】

#### Question

***

### 5.Buyer Supplier Relationship Strength (RS)
$$RBI_{itc} = \frac{1}{NS_{itc}}\sum_{j=1}^{NS_{itc}} \frac{Count\ of\ Nonzero\ Supplier\ Imports\ Month_{ijtc}}{Count\ of\ Nonzero\ Imports\ Month_{itc}}$$
$$RS_{it} = \frac{\sum_{c=1}^{NC_{it}}IV_{itc }\cdot RBI_{itc}}{\sum_{c=1}^{BC_{ii}}IV_{itc}}$$

* $NS_{itc}$ is the total number of suppliers from which category c is imported by firm i in year t【t 年 i 公司在货物 c 上有多少个供应商】【Panjiva】

* $Count\ of\ Nonzero\ Supplier\ Imports\ Month_{ijtc}$ is the total number of months in year t in which firm i imports category c from the supplier j, 【i 公司 t 年在 j 供应商 有几个月是进口的】【Panjiva】

* [ ] $Count\ of\ Nonzero\ Imports\ Month_{itc}$ is total number of months in year t in which firm i imports category c from any supplier【公司有几个月是从任意公司进口的】【Panjiva】.

***



## Panjiva data columns name            
```
"arrivaldate"     到达时间
"shpmtorigin"     发货地
"conultcompanyid" 收货方公司id
"hscode"          货物代码（取前6位）      
"quantity_sum"    某一货物个数
"weight_sum"      货物总重
"value_sum"       货物总价值
"record_count"    集装箱个数
"companyid"       公司的id"companyname"     公司的名称
"isocountry2"     发货公司的注册地
"gvkey"           公司代码
"activeflag"      
"crsp_flag" 
```


### double sort with ccc

#### What is CCC

* The cash conversion cycle (CCC) refers to the time span between the outlay of cash for purchases to the receipt of cash from sales. It is a widely used metric to gauge the effectiveness of a firm’s management and intrinsic need for external financing.

$$CCC = 365 \cdot (\frac{avg(Inventories)}{COGS}+\frac{avg(AccountsReceivables)}{Sales}-\frac{avg(AccountsPayables)}{COGS})$$
* Average inventory, average accounts receivables, and average accounts payables are calculated as the average of the beginning quarter and end of quarter levels. 
* The CCC is measured in days. It can be negative if DPO is longer than the sum of DIO and DRO.
