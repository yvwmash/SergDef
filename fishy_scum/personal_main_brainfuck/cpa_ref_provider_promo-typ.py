from inc import *
import inspect

# перешли от рекламодателей по промокоду
# список ссылок перехода,сводная
# сводная по (loangate	leads	sales_doubler	finline	admitad	doaffiliate	leadgid)


dt_b = date(year = 2019, month = 11,  day = 1)
dt_e = date(year = 2019, month = 11,  day = 30)

status, mq_conn = q_connect('front')
if status < 0:
 perror_exit()

q = f'''
SELECT
	date(cpa.created_at)                                                                as cpa_created_at, 
	cpa.provider_code                                                                   as cpa_provider, 
	if(cpa.user_type_id = 1, 'NEW', 'REPEAT')                                           as cpa_user_type,
	if(cpa.site_id = 1, 'creditup', 'bestcredit')                                       as cpa_site_credit,
	CONVERT(TRIM(JSON_UNQUOTE(JSON_EXTRACT(apps.extended, '$.promo_code'))) USING utf8)             as app_promo_code,
	CONVERT(TRIM(JSON_UNQUOTE(JSON_EXTRACT(apps.extended, '$.user_data.referral_utm'))) USING utf8) as app_ref,
	case 
		when apps.product_id IN (12, 23, 28, 29, 33, 35, 36, 42, 44, 52, 76, 77, 78, 79) then 'DISCOUNT'
		when apps.product_id IN (57, 58, 59, 60, 61, 62, 63, 64, 65)                     then 'FIX'
		when apps.product_id IN (1, 2, 10, 22, 25, 30, 31, 32)                           then 'FULL PRICE'
	else 'Err' end                                                                      as app_product_type
FROM finplugs_creditup_cpa_events cpa
inner join finplugs_creditup_applications apps on apps.id = cpa.application_id
WHERE 
	date(cpa.created_at) >= '{dt_b}' AND date(cpa.created_at) <= '{dt_e}'
	AND type_id = 1
'''
nrows, df = q_fetch(mq_conn, q)
q_close(mq_conn)

mask_has_promo_has_ref = (df.app_promo_code != '') & (df.app_ref != 'undefined')
df = df[mask_has_promo_has_ref].copy()

print(f'# has promo & has ref = {df_len(df)}')

re_baseref  = re.compile(r'((?:http://|https://)?.+?(?:/|$))')

df['app_base_ref']              = np.nan
df.app_base_ref                 = df.app_ref.str.extract(re_baseref, expand = false)

vrefs = df.app_base_ref.copy()
vrefs = vrefs[~vrefs.duplicated()]
vcpa  = df.cpa_provider.copy()
vcpa  = vcpa[~vcpa.duplicated()]

vtab = pd_df(index = vrefs, columns = vcpa)
for cpa in vcpa:
 for ref in vrefs:
  mask = (df.app_base_ref == ref) & (df.cpa_provider == cpa)
  n = df_len(df[mask])
  vtab.loc[ref, cpa] = n

fn = save_e('cpa_promos_aff', {
                               'cpa_promo_ref' : df,
                               'refs'          : pd_df(vrefs),
                               'by_ref'        : vtab,
                              },
           need_index = true, need_date = false
           )