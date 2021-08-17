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