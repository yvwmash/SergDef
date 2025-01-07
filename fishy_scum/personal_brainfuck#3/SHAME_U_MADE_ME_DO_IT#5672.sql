# apps no matter if it were actual loan
SELECT RIGHT(phone_mobile,10) as phone, 
       REPLACE(JSON_EXTRACT(extended, '$.promo_code'), '"', '') as promo_code,
		 created_at,
		 (select max(created_at)
		  from finplugs_creditup_applications
		  where status_id IN (4,5,6)
		    and user_id = apps.user_id
		    and apps.id > id
		    and date(created_at) >= dt_ploan_min and date(created_at) <= dt_loan_max
		 ) as prev_loan, # prev loan date
		 case 
		  when date(created_at) >= dt_loan_min and date(created_at) <= dt_loan_max and status_id IN (4,5,6) then 1 /* actual loan this month */
		 else 0 
		 end as actual_this_month
FROM pro_creditup_cab.finplugs_creditup_applications apps
WHERE date(created_at) >= '2018-08-01' AND date(created_at) <= CURDATE()
  and phone_mobile is not null