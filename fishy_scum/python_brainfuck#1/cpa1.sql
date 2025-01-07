SELECT
	provider_code, type_id, user_type_id, site_id, application_id, url, 
	MAX(date(created_at)) created_at, MAX(date(updated_at)) updated_at
FROM finplugs_creditup_cpa_events
WHERE 
	date(created_at) >= dt_min and date(created_at) <= dt_max
	AND type_id = 1
GROUP BY 
	application_id, provider_code, type_id, user_type_id, site_id, url
having application_id = max(application_id)
;