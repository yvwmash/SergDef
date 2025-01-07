SELECT 
	tb.*
FROM
	(SELECT 
	YEAR(ap.applied_at) yearof, MONTH(ap.applied_at) monthof, date(ap.applied_at) applied_date,
	id, user_id, applied_at,  product_id, product_dpr, credit_policy_id, if(cpa.cpa IS NULL, 0, 1) cpa,
	/*status_id, social_number, last_name, first_name, created_at, loan_amount, credit_policy_id,*/
	CONVERT(TRIM(JSON_UNQUOTE(JSON_EXTRACT(extended, '$.promo_code'))) USING utf8)                      as promo_code,
	CONVERT(TRIM(JSON_UNQUOTE(JSON_EXTRACT(extended, '$.user_data.utm_tags.utm_campaign'))) USING utf8) as utm_campaign,
	CONVERT(TRIM(JSON_UNQUOTE(JSON_EXTRACT(extended, '$.user_data.utm_tags.utm_medium'))) USING utf8)   as utm_medium,
	CONVERT(TRIM(JSON_UNQUOTE(JSON_EXTRACT(extended, '$.user_data.utm_tags.utm_source'))) USING utf8)   as utm_source,
	CONVERT(TRIM(JSON_UNQUOTE(JSON_EXTRACT(extended, '$.http_headers.host'))) USING utf8)               as host_name,
	CONVERT(TRIM(JSON_UNQUOTE(JSON_EXTRACT(extended, '$.user_data.referral_utm'))) USING utf8)          as app_ref,
	case 
		when ap.product_id IN (12, 23, 28, 29, 33, 35, 36, 42, 44, 52, 76, 77, 78, 79) then 'DISCOUNT'
  /* 83 2019-11-21б full price */
		when ap.product_id IN (57, 58, 59, 60, 61, 62, 63, 64, 65)                         then 'FIX'
		when ap.product_id IN (1, 2, 10, 22, 25, 30, 31, 32, 83)                           then 'FULL PRICE'
	ELSE 'Err' END product_type
	FROM finplugs_creditup_applications ap
		LEFT JOIN (SELECT distinct application_id, 1 AS cpa 
					FROM finplugs_creditup_cpa_events WHERE type_id = 1) cpa
					ON ap.id = cpa.application_id
	WHERE
		date(ap.applied_at) >= dt_min and date(ap.applied_at) <= dt_max
		AND status_id in (4,5,6)
	) tb
;