/* Minus black list from excel */
/*BLACK LIST*/
/*
SELECT DISTINCT user_id FROM creditup_dmaker.finplugs_pdl_blacklist_records WHERE status_id = 1;
*/

/*STOP LIST*/
/*
SELECT DISTINCT con.user_id FROM creditup_crm.creditup_crm_base_contacts con WHERE con.answer_id = 10;
*/

/*NOT ACTIVE*/
SELECT us.id, us.surname, us.name, us.email, right(us.phone,10) phone, 'noa' as typ
FROM pro_creditup_cab.users us
WHERE 
	us.is_activated = 0 AND 
	us.created_at >= dt_call_min AND us.created_at <= dt_call_max

union all

/*ACTIVE WITHOUT APPLICATION*/

SELECT 
	us.id, us.surname, us.name, us.email, right(us.phone,10) phone, 'awo' as typ
FROM 
	pro_creditup_cab.users us 
WHERE 
	us.is_activated = 1 AND 
	us.id NOT IN (SELECT DISTINCT user_id FROM pro_creditup_cab.finplugs_creditup_applications) AND 
	us.created_at >= dt_call_min AND us.created_at <= dt_call_max

union all

/* new - calceled */
SELECT 
	DISTINCT us.id, us.surname, us.name, us.email, right(us.phone,10) phone, 'nc' as typ
FROM 
	pro_creditup_cab.users us,
	pro_creditup_cab.finplugs_creditup_applications ap
WHERE 
	us.id = ap.user_id 
	AND ap.status_id IN (1, 7)  
	AND ap.user_id NOT IN (SELECT DISTINCT user_id FROM pro_creditup_cab.finplugs_creditup_applications
								  WHERE status_id IN (4,6)
								 )
	AND ap.created_at >= dt_call_min AND ap.created_at <= dt_call_max
;