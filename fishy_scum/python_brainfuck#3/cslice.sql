select social_number, count(*) as nloans
from finplugs_creditup_applications apps
where status_id in (4,5,6)
group by social_number
;