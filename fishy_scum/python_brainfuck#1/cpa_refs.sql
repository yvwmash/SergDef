/* СРА */
SELECT typ, u_id, name, lastname, app_id, app_status, created_at, f_loan, nloans,
       /*ref_is_before_registration, ref_created_at,*/ case when ref_from = 1 then 'creditUP' else 'bestcredit' end as ref_from,
       case when created_at = f_loan then 'первый' else 'повторный' end as is_first
FROM (
 SELECT 'by_cpa' as typ, apps.user_id AS u_id, apps.id AS app_id, us.name AS name, us.surname AS lastname,
        case when apps.status_id = 3 then 'approved' when apps.status_id = 4 then 'issued' when apps.status_id = 5 then 'closed' when apps.status_id = 6 then 'overdue' END AS app_status,
        apps.created_at as created_at,
        by_user.*,
        -1 as ref_is_before_registration, cpa.created_at as ref_created_at, site_id as ref_from
 FROM finplugs_creditup_cpa_events cpa
 INNER JOIN finplugs_creditup_applications apps ON apps.id = cpa.application_id
 INNER JOIN users us ON apps.user_id = us.id
 INNER JOIN (
  SELECT user_id, min(created_at) AS f_loan, COUNT(*) AS nloans 
  FROM finplugs_creditup_applications
  WHERE status_id IN (3,4,5,6) 
  GROUP BY user_id
 ) by_user ON by_user.user_id = apps.user_id
 WHERE apps.id = 973650
 ) cpa
union all
SELECT typ, u_id, name, lastname, app_id, app_status, created_at, f_loan, nloans,
       /*ref_is_before_registration,*/ /*ref_created_at,*/ ref_from,
       case when created_at = f_loan then 'первый' else 'повторный' end as is_first
from (
 select 'by_ref' as typ, apps.user_id AS u_id, apps.id AS app_id, us.name AS name, us.surname AS lastname,
         case when apps.status_id = 3 then 'approved' when apps.status_id = 4 then 'issued' when apps.status_id = 5 then 'closed' when apps.status_id = 6 then 'overdue' END AS app_status,
         apps.created_at as created_at,
         by_user.*,
         refs.is_before_registration as ref_is_before_registration, refs.created_at as ref_created_at, refs.utm_source as ref_from
 FROM finplugs_creditup_applications apps
 INNER JOIN users us ON us.id = apps.user_id
 INNER JOIN finplugs_creditup_referrals refs ON refs.user_id = us.id
 INNER JOIN (
  SELECT user_id, min(created_at) AS f_loan, COUNT(*) AS nloans 
  FROM finplugs_creditup_applications
  WHERE status_id IN (3,4,5,6) 
  GROUP BY user_id
 ) by_user ON by_user.user_id = apps.user_id
 WHERE apps.id = 973650
) ref
group by typ, u_id, name, lastname, app_id, app_status, f_loan, nloans, created_at
;