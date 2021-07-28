create database essence_of_life;

use essence_of_life;

drop table org_login;
drop table org_pnumber;
drop table hosp_pnumber;
drop table transplantation;
drop table organ_available;
drop table donor;
drop table patient;
drop table doctor;
drop table organisation;
drop table hospital;

create table hospital(
hospital_ID varchar(10) primary key,
hname varchar(200) NOT NULL,
head varchar(60),
first_address varchar(150) NOT NULL,
district varchar(50) NOT NULL,
state varchar(50) NOT NULL ,
pincode int(6),
constraint invalid_pincode check(length(pincode)=6)
); 

create table organisation(
org_ID varchar(10) primary key,
oname varchar(200) DEFAULT "Organ Bank",
head varchar(60),
first_address varchar(150) NOT NULL,
district varchar(50) NOT NULL,
state varchar(50) NOT NULL,
pincode int(6),
constraint invalid_pincode_for_organisation check(length(pincode)=6)
);

create table doctor(
doctor_ID varchar(10) primary key,
docname varchar(60) NOT NULL,
phone_num bigint(10) NOT NULL,
gender varchar(10),
dochosp_ID varchar(10) NOT NULL,
constraint invalid_doctor_phone_number check(phone_num between 6000000000 and 9999999999),
foreign key(dochosp_ID) references hospital(hospital_ID) on delete cascade on update cascade
);

create table patient(
patient_id varchar(12) primary key,
pname varchar(60) NOT NULL,
dateOfBirth date,
phone_num bigint(10) NOT NULL,
gender varchar(10),
bloodgroup varchar(8),
organ_required varchar(20) NOT NULL,
first_address varchar(150),
district varchar(50),
state varchar(50),
ptorg_ID varchar(10),
pthsp_ID varchar(10),
ptdoc_ID varchar(10),
constraint invalid_patient_aadharID check(length(patient_id)=12),
constraint invalid_patient_phone_number check(phone_num between 6000000000 and 9999999999),
foreign key(ptorg_ID) references organisation(Org_ID) on delete cascade on update cascade,
foreign key(pthsp_ID) references hospital(Hospital_ID) on delete set null on update cascade,
foreign key(ptdoc_ID) references doctor(Doctor_ID) on delete set null on update cascade
);

alter table patient add preport text;

create table donor(
donor_id varchar(12) primary key,
dname varchar(60) NOT NULL,
dateOfBirth date,
phone_num bigint(10) NOT NULL,
gender varchar(10),
bloodgroup varchar(8),
first_address varchar(150),
district varchar(50),
state varchar(50),
dnrorg_ID varchar(10),
constraint invalid_donor_aadharID check(length(donor_id)=12),
constraint invalid_donor_phone_number check(phone_num between 6000000000 and 9999999999),
foreign key(dnrorg_ID) references organisation(Org_ID) on delete cascade on update cascade
);

alter table donor add dreport text;

create table organ_available(
dnr_ID varchar(12),
organ_no varchar(3) default "1",
organtype varchar(30) NOT NULL,
typeofdonation varchar(20),
expiry datetime,
primary key(dnr_ID,organ_no),
foreign key(dnr_ID) references donor(donor_ID) on delete cascade on update cascade
);

alter table organ_available auto_increment=1;

create table transplantation(
trplant_ID int auto_increment primary key,
trdate date,
trstatus varchar(9) NOT NULL,
dnr_ID varchar(12),
organ_no varchar(3),
pnt_ID varchar(12),
foreign key(dnr_ID,organ_no) references organ_available(dnr_ID,organ_no) on delete cascade on update cascade,
foreign key(pnt_ID) references patient(patient_ID) on delete cascade on update cascade
);

alter table transplantation auto_increment=1001;
alter table transplantation alter organ_no set default '1';

create table hosp_pnumber(
hid varchar(10),
phone_num bigint(10) NOT NULL,
foreign key(hid) references hospital(hospital_ID) on delete cascade on update cascade
);

create table org_pnumber(
oid varchar(10),
phone_num bigint(10) NOT NULL,
foreign key(oid) references organisation(org_ID) on delete cascade on update cascade
);

create table org_login(
login_id varchar(10) primary key,
pswd varchar(150) NOT NULL,
constraint length_of_password_is_less_than_8 check(length(pswd)>=8),
foreign key(login_id) references organisation(org_ID) on delete cascade on update cascade
);

alter table org_login add oemail varchar(150);
alter table org_login add opstatus varchar(10) DEFAULT "o";

create table govt_login(
login_id varchar(60) primary key,
pswd varchar(150) NOT NULL,
constraint length_of_password_is_invalid check(length(pswd)>=8)
);

alter table govt_login add email varchar(150) NOT NULL;
alter table govt_login add state varchar(100) NOT NULL;
alter table govt_login add pstatus varchar(10) DEFAULT "o";

insert into govt_login values ("kar.organbank", "12345678");