--alter table gm_containertracker add column shippingline_id varchar(50) null;
--alter table gm_containertracker add column ib_dispatch_dt int null;
--alter table gm_containertracker add column no_of_containers int null;
--alter table gm_containertracker add column cts_created_date  datetime  null;
--alter table gm_containertracker modify container_no varchar(50) null;
--alter table gm_containertracker modify seal_no varchar(50) null;
--alter table gm_containertracker add column submitted_by varchar(50) null;

--alter table gm_containertracker drop column ib_dispatch_dt ;
--alter table gm_containertracker add column ib_dispatch_dt datetime null;

For epc
IN bajaj db; 
update gm_bomplate set plate_image = concat("qa/bajaj/plates/", plate_id, ".png") ;
update gm_bomplate set plate_image_with_part = concat("qa/bajaj/plates_with_part/", plate_id, ".png") ;

IN bajajcv and probiking
update gm_bomplate set plate_image = concat("qa/bajaj/plates/", plate_id, ".PNG") ;
update gm_bomplate set plate_image_with_part = concat("qa/bajaj/plates_with_part/", plate_id, ".PNG") ;

--alter table gm_bomvisualization add column status varchar(25) null;
--alter table gm_bomvisualization add column published_date datetime null;
--alter table gm_bomvisualization add column remarks varchar(500) null;

--alter table gm_userprofile add column reset_password boolean default false;
--alter table gm_userprofile add column reset_date datetime null;

--alter table gm_producttype add column overview varchar(512) null;
--alter table gm_producttype add brand_id integer;
--alter table gm_producttype add foreign key (brand_id) references gm_producttype(id);

--alter table gm_manufacturingdata add column is_discrepant bool default 0;
--alter table gm_manufacturingdata add column sent_to_sap bool default 0;

--alter table gm_containerindent drop foreign key `transporter_id_refs_id_52bca095`;
--alter table gm_containerindent drop column transporter_id;
--alter table gm_containerlr add column transporter_id integer;
--alter table gm_containerlr add foreign key (transporter_id) references gm_transporter(id);
--update gm_containerlr new inner join gm_containertracker old on old.transaction_id=new.transaction_id set new.transporter_id=old.transporter_id;

--alter table gm_brandproductrange drop column vertical;

alter table gm_brand drop column image_url;
alter table gm_brand add column image_url varchar(255) null;

--------------- RUN ONLY IN AFTERBUY---------
rename table gm_constant to afterbuy_constant;
---------------------------------------------

--alter table afterbuy_userproduct add column is_accepted boolean default false;	
--alter table afterbuy_userproduct add column service_reminder int null;
--alter table afterbuy_userproduct add column details_completed int null;
--alter table afterbuy_userproduct add column manual_link varchar(512) null;
--alter table afterbuy_userproduct drop foreign key `brand_id_refs_id_e5504abf`;
--alter table afterbuy_userproduct drop column brand_id;
--alter table afterbuy_userproduct drop column nick_name;
--alter table afterbuy_userproduct add column nick_name varchar(100) null;
--alter table afterbuy_userproduct add column warranty_year datetime null;
--alter table afterbuy_userproduct add column insurance_year datetime null;
--alter table afterbuy_userproduct drop column image_url;
--alter table afterbuy_userproduct add column image_url varchar(255) null;

--alter table afterbuy_consumer drop index phone_number;
--alter table afterbuy_consumer add column is_phone_verified boolean default false;
--alter table afterbuy_consumer drop column image_url;
--alter table afterbuy_consumer add column image_url varchar(255) null;
--alter table afterbuy_consumer add column is_phone_verified boolean default false;
--alter table afterbuy_consumer add column has_discrepancy boolean default False;
--alter table afterbuy_consumer add column last_sync_date datetime null;

--alter table afterbuy_producttype add brand_id integer;
--alter table afterbuy_producttype add foreign key (brand_id) references afterbuy_producttype(id);
--alter table afterbuy_producttype add column overview varchar(512) null;

--alter table afterbuy_brand drop column image_url;
--alter table afterbuy_brand add column image_url varchar(255) null;

--alter table afterbuy_usermobileinfo add column brand varchar(50) null;
--alter table afterbuy_usermobileinfo add column mac_address varchar(100) null;
--alter table afterbuy_usermobileinfo add column network_provider varchar(100) null;
--alter table afterbuy_usermobileinfo add column total_memory double null;
--alter table afterbuy_usermobileinfo add column available_memory double null;

--------------------------------------------------------------------------------------------
--alter table gm_bomheader add column revision_number int default 0;
--
--alter table gm_bomvisualization modify column x_coordinate int default 0;
--alter table gm_bomvisualization modify column y_coordinate int default 0;
--alter table gm_bomvisualization modify column z_coordinate int default 0;
--
--alter table gm_bomheader add column eco_number varchar(20) null;

--alter table gm_retailer add column is_active boolean default True;
--alter table gm_retailer add column approved boolean default False;
--alter table gm_dealer add column sm_id integer;
--alter table gm_dealer add foreign key(sm_id) references gm_areasalesmanager(id);
--alter table auth_user modify username varchar(250);
--alter table gm_comment modify column comment varchar(512);
--------------------------------------------------------------------------------------------
DROP INDEX constant_name ON gm_constant;

alter table gm_bomvisualization drop column status;
alter table gm_bomvisualization add column is_published boolean default False;
alter table gm_bomvisualization add column is_approved boolean default False;


--------------------------bajajcv------------------------------------------------------------
alter table gm_dealer add column asm_id integer
alter table gm_dealer add foreign key(asm_id) references gm_areaservicemanager(id);
alter table gm_dealer add column area varchar(250);
alter table gm_dealer add column last_transaction_date datetime null;
alter table gm_dealer add column regional_office varchar(250);
---------------------------------------------------------------------------------------------

ALTER TABLE gm_bomvisualization ADD is_published tinyint(1)  NOT NULL DEFAULT 0;
ALTER TABLE gm_bomvisualization ADD is_approved tinyint(1)  NOT NULL DEFAULT 0;


