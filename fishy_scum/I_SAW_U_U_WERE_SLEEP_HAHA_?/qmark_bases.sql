/* 
 Выборка для Романа. Маркетинг. Ежедневно.
 1. Клиенты с закрытыми кредитами.
 2. Клиенты у которых кредит заканчивается через три дня от текущей даты.
 3. Клиенты с открытыми кредитами. Статистика.
 Список, Excel
*/

/* Клиенты с закрытыми кредитами. Предложение */
SELECT
	us.id, us.surname, us.name, us.email, right(us.phone,10) phone, date(us.activated_at),
	MAX(apl.overdue_days) overdue_days_max,
	(SELECT date(MIN(applied_at)) FROM finplugs_creditup_applications WHERE user_id = us.id AND status_id IN (3,4,5,6)) AS first_credit,
	COUNT(apl.id) count_loans,
	MAX(if(apl.closed_at IS NULL OR apl.closed_at = '0000-00-00 00:00:00', apl.billing_updated_at, apl.closed_at)) closed_at, 
	MIN(DATEDIFF(CURDATE(), 
		if(apl.closed_at IS NULL OR apl.closed_at = '0000-00-00 00:00:00', apl.billing_updated_at, apl.closed_at))) daysago,
	MAX(case 
		when user_id IN (SELECT DISTINCT user_id FROM pro_creditup_cab.finplugs_creditup_applications WHERE status_id = 2)
		then 1 ELSE 0 END
		) was_rejected
FROM 
	pro_creditup_cab.finplugs_creditup_applications apl,
	pro_creditup_cab.users us
WHERE 
	apl.user_id = us.id
	AND apl.status_id = 5 
	AND apl.applied_at < CURDATE()
	AND apl.user_id NOT IN (SELECT DISTINCT user_id FROM pro_creditup_cab.finplugs_creditup_applications WHERE status_id IN (3,4,6))
GROUP BY 
	us.id, us.surname, us.name, us.email, right(us.phone,10)
;


/* Клиенты у которых кредит заканчивается через три дня от текущей даты. */
SELECT 
	us.id as u_id, us.surname, us.name, us.email, right(us.phone,10) as phone, us.activated_at,
	apl.id as app_id, apl.status_id, apl.applied_at, apl.loan_days, apl.overdue_days, 
	apl.prolongation_total_days, apl.payment_date
FROM 
	pro_creditup_cab.finplugs_creditup_applications apl,
	pro_creditup_cab.users us
WHERE 
	apl.user_id = us.id
	AND status_id = 4
	AND payment_date = CURDATE() + INTERVAL 3 DAY
;

/* Клиенты с открытыми кредитами. */
SELECT apps_in_credit.user_id,
       users.name, users.surname, 
       right(users.phone,10) phone, users.email,
       apps_successful.min_app_date,
		 apps_successful.max_app_date,
		 apps_successful.nloans,
		 apps_successful.loan_overdues,
		 case when apps_successful.loan_overdues > 0 then 1 ELSE 0 END AS is_overduer,
		 apps_successful.ndays_in_credits,
		 apps_successful.overdue_days_sum,
		 users.activated_at activated_at
FROM (
 SELECT user_id, applied_at FROM finplugs_creditup_applications WHERE status_id IN (3,4,6) GROUP BY user_id
) apps_in_credit
LEFT OUTER JOIN (
 SELECT user_id, 
        COUNT(*) nloans, 
		  SUM(loan_overdue) loan_overdues,
		  ifnull(SUM(overdue_days),0) + ifnull(SUM(loan_days),0) + ifnull(SUM(prolongation_total_days),0) AS ndays_in_credits,
		  SUM(overdue_days) overdue_days_sum,
        MIN(applied_at) min_app_date,
		  MAX(applied_at) max_app_date
 FROM finplugs_creditup_applications 
 WHERE status_id IN (3,4,5,6) 
 GROUP BY user_id
) apps_successful ON apps_in_credit.user_id = apps_successful.user_id
INNER JOIN users ON apps_in_credit.user_id = users.id
WHERE apps_in_credit.applied_at >= '2019-01-01' AND apps_in_credit.applied_at < CURDATE()
GROUP BY apps_in_credit.user_id,
         users.name, users.surname, 
         right(users.phone,10), users.email,
         apps_successful.min_app_date,
         apps_successful.max_app_date,
         apps_successful.nloans, 
			apps_successful.loan_overdues, 
			apps_successful.ndays_in_credits, 
			case when apps_successful.loan_overdues > 0 then 1 ELSE 0 END,
         apps_successful.overdue_days_sum,
         users.activated_at
;