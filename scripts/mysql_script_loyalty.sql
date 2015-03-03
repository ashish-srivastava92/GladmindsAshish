
ALTER TABLE bajaj_mechanic ADD sent_sms boolean default false;

alter table bajaj_productcatalog add column image_url varchar(255) null;
alter table bajaj_productcatalog add column partner_id integer;
alter table bajaj_productcatalog  add foreign key (partner_id) references bajaj_partner(id);

alter table bajaj_redemptionrequest add column owner_id integer;
alter table bajaj_redemptionrequest add foreign key (owner_id) references bajaj_partner(id);
alter table bajaj_redemptionrequest add column packed_by varchar(50) null;
alter table bajaj_redemptionrequest add column image_url varchar(255) null
alter table bajaj_redemptionrequest add column refunded_points bool default 0;
alter table bajaj_redemptionrequest add column due_date datetime;
alter table bajaj_redemptionrequest add column resolution_flag boolean;

alter table bajaj_partner add column name varchar(100) null;
alter table bajaj_welcomekit add column resolution_flag boolean;

#########################################V.0.1.5#############################################################
alter table bajaj_mechanic add column sent_to_sap bool default 0;
alter table bajaj_mechanic add column middle_name varchar(50) null;
alter table bajaj_mechanic add column adress_line_1 varchar(40) null;
alter table bajaj_mechanic add column adress_line_2 varchar(40) null;
alter table bajaj_mechanic add column adress_line_3 varchar(40) null;
alter table bajaj_mechanic add column adress_line_4 varchar(40) null;
alter table bajaj_mechanic add column adress_line_5 varchar(40) null;
alter table bajaj_mechanic add column adress_line_6 varchar(40) null;
alter table bajaj_mechanic add column download_detail bool default 0;
alter table bajaj_mechanic add permanent_id char(50) default null;
alter table bajaj_mechanic add constraint unique_id unique(permanent_id);

alter table bajaj_mechanic add column dob date;
update bajaj_mechanic set dob=date_of_birth;
alter table bajaj_mechanic drop column date_of_birth;
alter table bajaj_mechanic add column date_of_birth date;
update bajaj_mechanic set date_of_birth=dob;
alter table bajaj_mechanic drop column dob;

#############################################V.0.1.6##########################################################

alter table bajaj_redemptionrequest add column approved_date datetime;
alter table bajaj_redemptionrequest add column shipped_date datetime;
alter table bajaj_redemptionrequest add column delivery_date datetime;
alter table bajaj_redemptionrequest add column pod_number varchar(50) null;
alter table bajaj_welcomekit add column shipped_date datetime;
alter table bajaj_welcomekit add column delivery_date datetime;
alter table bajaj_welcomekit add column pod_number varchar(50) null;
alter table bajaj_accumulationrequest add column is_transferred boolean default false;
alter table bajaj_mechanic drop column adress_line_1;
alter table bajaj_mechanic drop column adress_line_2;
alter table bajaj_mechanic drop column adress_line_3;
alter table bajaj_mechanic drop column adress_line_4;
alter table bajaj_mechanic drop column adress_line_5;
alter table bajaj_mechanic drop column adress_line_6;

alter table bajaj_mechanic add column address_line_1 varchar(40) null;
alter table bajaj_mechanic add column address_line_2 varchar(40) null;
alter table bajaj_mechanic add column address_line_3 varchar(40) null;
alter table bajaj_mechanic add column address_line_4 varchar(40) null;
alter table bajaj_mechanic add column address_line_5 varchar(40) null;
alter table bajaj_mechanic add column address_line_6 varchar(40) null;

###################################################################################################
rename table bajaj_areasalesmanager to bajaj_areasparesmanager;
rename table bajaj_nationalsalesmanager to bajaj_nationalsparesmanager;
update auth_group set name="AreaSparesManagers" where name="AreaSalesManagers";
update auth_group set name="NationalSparesManagers" where name="NationalSalesManagers";

alter table bajaj_redemptionrequest add column points integer(50) null;
alter table bajaj_nationalsparesmanager add foreign key (territory_id) references bajaj_territory(id);
alter table bajaj_areasparesmanager add foreign key (state_id) references bajaj_state(id);
alter table bajaj_mechanic add foreign key (state_id) references bajaj_state(id);

insert into bajaj_areasparesmanager (areasparesmanager_id, statae_id) 
select bajaj_areasparesmanager.id, bajaj_state.id from bajaj_areasparesmanager
inner join bajaj_state on bajaj_state.state_name = bajaj_areasparesmaanager.state;

insert into bajaj_nationalsparesmanager (nationalsparesmanager_id, territory_id) 
select bajaj_nationalsparesmanager.id, bajaj_territory.id from bajaj_nationalsparesmanager 
inner join bajaj_territory on bajaj_territory.territory = bajaj_nationalsparesmanager.territory;

alter table bajaj_nationalsparesmanager drop column territory;
alter table bajaj_areasparesmanager drop column state ;

update table bajaj_mechanic 
inner join bajaj_state on bajaj_state.state_name = bajaj_mechanic.state 
set bajaj_mechanic.state_id = bajaj_state.id 
where bajaj_state.state_name = 'Karnataka';


update table bajaj_mechanic 
inner join bajaj_state on bajaj_state.state_name = bajaj_mechanic.state 
set bajaj_mechanic.state_id = bajaj_state.id 
where bajaj_state.state_name = 'Tamil Nadu';

update table bajaj_mechanic 
inner join bajaj_state on bajaj_state.state_name = bajaj_mechanic.state 
set bajaj_mechanic.state_id = bajaj_state.id 
where bajaj_state.state_name = 'Kerala';

alter table bajaj_mechanic drop column state;

