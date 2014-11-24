INSERT INTO `auth_group` VALUES (4,'ascs'),(3,'customer'),(1,'dealers'),(2,'sas');

"run migrate dealer, asc and service advisor"

insert into bajaj.bajaj_asctempregistration(id,name,password,phone_number,email,address,pincode,timestamp,dealer_id) select aftersell_ascsaveform.id, aftersell_ascsaveform.name, aftersell_ascsaveform.password, aftersell_ascsaveform.phone_number,aftersell_ascsaveform.email,aftersell_ascsaveform.address, aftersell_ascsaveform.pincode,aftersell_ascsaveform.timestamp, aftersell_ascsaveform.dealer_id  from aftersell_ascsaveform;

insert into bajaj.bajaj_satempregistration(id,name,phone_number,status) select gladminds_sasaveform.id, gladminds_sasaveform.name, gladminds_sasaveform.phone_number,gladminds_sasaveform.status from gladminds_sasaveform;

insert into bajaj.bajaj_smslog(id, created_date, modified_date, action, message, sender, receiver) select aftersell_auditlog.id, aftersell_auditlog.date, aftersell_auditlog.date, aftersell_auditlog.action,aftersell_auditlog.message, aftersell_auditlog.sender, aftersell_auditlog.reciever from aftersell_auditlog;

insert into bajaj.bajaj_datafeedlog(data_feed_id, feed_type, total_data_count, failed_data_count, success_data_count, action, status, timestamp, remarks, file_location ) select aftersell_datafeedlog.data_feed_id, aftersell_datafeedlog.feed_type, aftersell_datafeedlog.total_data_count, aftersell_datafeedlog.failed_data_count, aftersell_datafeedlog.success_data_count, aftersell_datafeedlog.action, aftersell_datafeedlog.status, aftersell_datafeedlog.timestamp, aftersell_datafeedlog.remarks, aftersell_datafeedlog.file_location  from aftersell_datafeedlog;

insert into bajaj.bajaj_messagetemplate(id,template_key,template,description) select gladminds_messagetemplate.id, gladminds_messagetemplate.template_key, gladminds_messagetemplate.template, gladminds_messagetemplate.description from gladminds_messagetemplate;

insert into bajaj.bajaj_emailtemplate(id,template_key,sender,receiver,subject,body,description) select gladminds_emailtemplate.id, gladminds_emailtemplate.template_key, gladminds_emailtemplate.sender, gladminds_emailtemplate.reciever, gladminds_emailtemplate.subject, gladminds_emailtemplate.body, gladminds_emailtemplate.description from gladminds_emailtemplate;

insert into bajaj.bajaj_producttype(id,product_type,image_url,is_active) select gladminds_producttypedata.product_type_id, gladminds_producttypedata.product_type,gladminds_producttypedata.product_image_loc,gladminds_producttypedata.isActive from gladminds_producttypedata;

alter table bajaj_oldfscdata change `product_id` `product_id` int(11) default null;

"
set the env varibales (QA)

export DB_USER='gladminds'
export DB_PASSWORD='gladmindsqa2'
export DB_HOST='gladminds-qa-2.chnnvvffqwop.us-east-1.rds.amazonaws.com'
export MIGRATE_DB='gladminds'
export OFFSET=0

Run these commands
nohup python scripts/migrate_dealer_data.py &
nohup python scripts/migrate_asc_data.py &
nohup python scripts/migrate_service_advisor.py &

nohup python scripts/migrate_products.py &
nohup python scripts/migrate_coupons.py &
nohup python scripts/migrate_coupons_sa_relations.py &

nohup python scripts/migrate_old_fsc.py &
nohup python scripts/migrate_temp_customer.py &
nohup python scripts/migrate_ucn_recovery.py &
