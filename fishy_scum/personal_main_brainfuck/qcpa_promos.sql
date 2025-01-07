select * 
from (
 SELECT
 	YEAR(cpa.created_at)             as cpa_yearof, 
 	MONTH(cpa.created_at)            as cpa_monthof, 
 	date(cpa.created_at)             as cpa_dateof, 
 	cpa.provider_code                                                                   as cpa_provider, 
 	if(cpa.user_type_id = 1, 'NEW', 'REPEAT')                                           as cpa_user_type,
 	if(cpa.site_id = 1, 'creditup', 'bestcredit')                                       as cpa_site_credit,
 	CONVERT(TRIM(JSON_UNQUOTE(JSON_EXTRACT(apps.extended, '$.promo_code')))             USING utf8) as app_promo_code,
  CONVERT(TRIM(JSON_UNQUOTE(JSON_EXTRACT(apps.extended, '$.user_data.referral_utm'))) USING utf8)   as ref_utm,
 	case 
 		when apps.product_id IN (12, 23, 28, 29, 33, 35, 36, 42, 44, 52, 76, 77, 78, 79) then 'DISCOUNT'
 		when apps.product_id IN (57, 58, 59, 60, 61, 62, 63, 64, 65)                     then 'FIX'
 		when apps.product_id IN (1, 2, 10, 22, 25, 30, 31, 32)                           then 'FULL PRICE'
 	else 'Err' end                                                                      as app_product_type
 FROM finplugs_creditup_cpa_events cpa
 inner join finplugs_creditup_applications apps on apps.id = cpa.application_id
 WHERE 
 	date(cpa.created_at) >= '2019-01-01' AND date(cpa.created_at) <= '2019-10-31'
 	AND type_id = 1
) i
where i.app_promo_code is not null