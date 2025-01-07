
#########################################################################################################

create table c_types (
 id           serial,
 c_date       date,
 c_text       text,
 c_time       time,
 c_timestamp  timestamp,
 c_money      money,
 c_float      float
);

insert into c_types(c_date,c_text,c_time,c_timestamp,c_money,c_float) values
('2019-09-01', 'text0', '00:00:01', timestamp '2019-09-01 20:00:00', 1000.0001, 1000.0001),
('2019-09-01', 'text1', '00:00:02', timestamp '2019-09-01 21:00:00', 2000.0001, 2000.0001)
;

select * from c_types;

# id |   c_date   | c_text |  c_time  |     c_timestamp     |    c_money    |  c_float  
#----+------------+--------+----------+---------------------+---------------+-----------
#  1 | 2019-09-01 | text0  | 00:00:01 | 2019-09-01 20:00:00 |  1 000,00грн. | 1000.0001
#  2 | 2019-09-01 | text1  | 00:00:02 | 2019-09-01 21:00:00 |  2 000,00грн. | 2000.0001

drop table c_types;

create table c_order (
 s text
);

insert into c_order(s) values
('а'),
('п'),
('я'),
('ё'),
('А'),
('a'),
('y'),
('x'),
('_абц'),
('    абц'),
('  abc'),
('-abc')
;

select * from c_order;
select * from c_order order by s;

drop table c_order;