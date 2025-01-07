select pays.user_id                                                  as uid,
       apps.first_name                                               as f_nm,
       apps.last_name                                                as s_nm,
       apps.other_name                                               as t_nm,
       sum(pays.amount)                                              as paid,
       group_concat(distinct pays.application_id separator ', ')     as apps,
       group_concat(distinct apps.social_number separator ', ')      as inns
from finplugs_creditup_payments pays
inner join finplugs_creditup_applications apps on apps.id = pays.application_id
where date(paid_at) >= dt_min and date(paid_at) <= dt_max
  and pays.payment_type_id in (2,3)
  and pays.status_id = 3
  and is_autopayment = 1
group by pays.user_id, apps.first_name, apps.last_name, apps.other_name