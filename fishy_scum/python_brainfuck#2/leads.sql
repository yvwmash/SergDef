select concat(case when first_name is null then '' else concat(first_name, ' ') end,
              case when last_name  is null then '' else        last_name        end,
				  case when other_name is null then '' else concat(' ', other_name) end
				 ) as full_nm,
       phone_mobile as phone
from finplugs_creditup_applications apps
where status_id = 6 # overdue
      and phone_mobile is not null
      and created_at > '2019-01-01'
order by full_nm
limit 1000