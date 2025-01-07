SELECT
	YEAR(created_at) yearof, MONTH(created_at) monthof, date(created_at) dateof, 
	provider_code provider, 
	if(user_type_id = 1, 'NEW', 'REPEAT') user_type,
	if(site_id = 1, 'creditup', 'bestcredit') site_credit,
	COUNT(DISTINCT application_id) napplications	
FROM finplugs_creditup_cpa_events
WHERE 
	date(created_at) >= dt_min AND date(created_at) <= dt_max
	AND type_id = 1
GROUP BY
	YEAR(created_at), MONTH(created_at), date(created_at), 
	provider_code, 
	if(user_type_id = 1, 'NEW', 'REPEAT'),
	if(site_id = 1, 'creditup', 'bestcredit')
;
