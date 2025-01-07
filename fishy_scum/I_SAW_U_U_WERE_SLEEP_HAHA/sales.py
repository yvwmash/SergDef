# -*- coding: utf-8 -*-

# python3 sales.py <файл промокодов>
# <файл промокодов> - добавлять вручную из списка Романа

from inc import *
import inspect

def perror_exit(e_code = -1):
 print(' * line: ',inspect.currentframe().f_back.f_lineno)
 exit(e_code)

if argc < 2:
 print('usage: python sales.py <promos>')
 sys.exit(0)
if argc == 2:
 fp = argv[1]

cpas = ['admitad', 'doaff', 'finlead', 'finline', 'leadgid', 'leadssu', 'linkprofit', 'loangate', 'primelead', 'sd']

promos            = pd.read_excel(fp, dtype = str, encoding = 'utf-8', index_col = none)
promos.promo_code = promos.promo_code.str.lower()
promos            = promos.set_index('promo_code')

# query
status, mq_conn = q_connect('front')
if status < 0:
 perror_exit()

# SQL date params
YEAR     = 2019
MONTH    = 11
LAST_DAY = last_day(YEAR, MONTH)

max_date = date(year = YEAR, month = MONTH,  day = LAST_DAY)
min_date = date(year = YEAR, month = MONTH,  day = 1)

rq = read_f('qsales.sql')
rq = rq.replace('dt_min',  "'" + str(min_date) + "'")
rq = rq.replace('dt_max',  "'" + str(max_date) + "'")
print('query')
nrows, list = q_fetch(mq_conn, rq)
q_close(mq_conn)

df_conv(list, 
       {'yearof'           : 'int',
        'monthof'          : 'int',
        'cpa'              : 'int',
        'applied_date'     : 'date',
        'id'               : 'int',
        'user_id'          : 'int',
        'applied_at'       : 'date',
        'product_id'       : 'int',
        'product_dpr'      : 'float',
        'credit_policy_id' : 'int',
})

list.utm_source = list.utm_source.str.lower()
list.promo_code = list.promo_code.str.lower()

list['channel']  = np.nan
list['discount'] = np.nan

print('# = ', df_len(list))

#list.loc[list.utm_source.isin(cpas), 'cpa'] = 1

## channels
# promo list
list = list.set_index('promo_code')
list.update(promos)
list = list.reset_index()
promo = list.loc[list.channel.notna()].copy()
mask_cpa       = promo.cpa == 1
mask_cpa_slash = (promo.channel.isin(['EMAIL','PUSH','FB'])) & mask_cpa
list = df_minus(list, promo)

# known channel
mask_k_ch = list.utm_source.str.contains(r'esputnik-promo|creditup|email|push|fb|facebook', na = false)
k_ch = list.loc[mask_k_ch].copy()
mask_mail = k_ch.utm_source.str.contains(r'esputnik-promo|creditup|email')
mask_push = k_ch.utm_source.str.contains(r'push')
mask_fb   = k_ch.utm_source.str.contains(r'fb|facebook')
k_ch.loc[mask_mail, 'channel'] = 'EMAIL'
k_ch.loc[mask_push, 'channel'] = 'PUSH'
k_ch.loc[mask_fb,   'channel'] = 'FB'
list = df_minus(list, k_ch)

# callc promo
mask_icallc = list.promo_code.str.contains(r'^(?:f|r)\d{8}$', na = false)
mask_rcallc = list.promo_code.str.contains(r'^(?:\d{6})|(?:r\d{4})$', na = false)
icallc = list.loc[mask_icallc].copy()
rcallc = list.loc[mask_rcallc].copy()
icallc.loc[:,'channel'] = 'EMAIL'
rcallc.loc[:,'channel'] = 'EMAIL'
list = df_minus(list, icallc)
list = df_minus(list, rcallc)

# cpa
mask_cpa = list.cpa == 1
cpa = list[mask_cpa].copy()
cpa.loc[mask_cpa, 'channel'] = 'CPA'
list = df_minus(list, cpa)

# picodi
mask_picodi = list.promo_code.str.contains(r'^picodi$', na = false)
picodi = list[mask_picodi].copy()
picodi.loc[:, 'channel'] = 'EMAIL'
list = df_minus(list, picodi)

# tail discount
tail = list[(list.product_type == 'DISCOUNT') & list.channel.isna()].copy()
tail.channel  = 'EMAIL'
tail.discount = 'EMAIL UTM'
list = df_minus(list, tail)

# ETC
list.loc[:, 'channel'] = 'ETC'

# union
l = pd.concat([promo,k_ch,icallc,rcallc,cpa,picodi,tail,list], axis = 'index')

# cpa with slashes
mask_cpa = l.cpa == 1
mask_m   = (l.channel == 'EMAIL') & mask_cpa
mask_p   = (l.channel == 'PUSH')  & mask_cpa
mask_f   = (l.channel == 'FB')    & mask_cpa
mask_cpa = mask_cpa & ~(mask_m|mask_p|mask_f)
l.loc[mask_m, 'channel']   = 'CPA / EMAIL'
l.loc[mask_p, 'channel']   = 'CPA / PUSH'
l.loc[mask_f, 'channel']   = 'CPA / FB'
l.loc[mask_cpa, 'channel'] = 'CPA'

## promo types
# discount
p = l[l.product_type == 'DISCOUNT'].copy()
l = df_minus(l,p)

# callc
mask_icallc = p.promo_code.str.contains(r'^(?:f|r)\d{8}$', na = false)
mask_rcallc = p.promo_code.str.contains(r'^(?:\d{6})|(?:r\d{4})$', na = false)
p.loc[mask_icallc, 'discount'] = 'CALLCENTER PROMO'
p.loc[mask_rcallc, 'discount'] = 'REMOTE PROMO'

# picodi
mask_picodi = p.promo_code.str.contains('picodi', na = false)
p.loc[mask_picodi, 'discount'] = 'PICODI PROMO'

# email/FB/PUSH
mask_tail = ~(mask_icallc|mask_rcallc|mask_picodi)
mask_mail   = p.channel == 'EMAIL'
mask_mail_s = p.channel == 'CPA / EMAIL'
mask_push   = p.channel == 'PUSH'
mask_push_s = p.channel == 'CPA / PUSH'
mask_fb     = p.channel == 'FB'
mask_fb_s   = p.channel == 'CPA / FB'
p.loc[mask_tail & mask_mail,   'discount'] = 'EMAIL PROMO'
p.loc[mask_tail & mask_mail_s, 'discount'] = 'EMAIL PROMO'
p.loc[mask_tail & mask_push,   'discount'] = 'PUSH PROMO'
p.loc[mask_tail & mask_push_s, 'discount'] = 'PUSH PROMO'
p.loc[mask_tail & mask_fb,     'discount'] = 'FB PROMO'
p.loc[mask_tail & mask_fb_s,   'discount'] = 'FB PROMO'

# EMAIL UTM
mask_tail = p.discount.isna()
p.loc[mask_tail, 'discount'] = 'EMAIL UTM'

l = pd.concat([l,p], axis = 'index')
# rearrange columns
l = l[['yearof','monthof','applied_date','applied_at',
       'id','user_id',
       'product_id','product_dpr','credit_policy_id',
       'cpa','utm_campaign','utm_medium','utm_source','host_name', 'app_ref',
       'promo_code','product_type','channel','discount']]
print('# res = ', df_len(l))

# group ###############################################################################################################

m_ch_cpa    = l.channel == 'CPA'
m_ch_cpa_e  = l.channel == 'CPA / EMAIL'
m_ch_cpa_fb = l.channel == 'CPA / FB'
m_ch_cpa_p  = l.channel == 'CPA / PUSH'
m_ch_e      = l.channel == 'EMAIL'
m_ch_etc    = l.channel == 'ETC'
m_ch_fb     = l.channel == 'FB'
m_ch_p      = l.channel == 'PUSH'
m_d_c       = l.discount == 'CALLCENTER PROMO'
m_d_e       = l.discount == 'EMAIL PROMO'
m_d_eu      = l.discount == 'EMAIL UTM'
m_d_fb      = l.discount == 'FB PROMO'
m_d_p       = l.discount == 'PUSH PROMO'
m_d_r       = l.discount == 'REMOTE PROMO'
m_d_pic     = l.discount == 'PICODI PROMO'
m_d_fix     = l.product_type == 'FIX'
m_d_full    = l.product_type == 'FULL PRICE'

vch = ['CPA','CPA / EMAIL','CPA / FB','CPA / PUSH','EMAIL','ETC','FB','PUSH']
vdi = ['CALLCENTER PROMO','EMAIL PROMO','EMAIL UTM','FB PROMO',
       'PUSH PROMO','REMOTE PROMO','PICODI PROMO','FIX','FULL PRICE']

dch = {
'CPA'        : m_ch_cpa,
'CPA / EMAIL': m_ch_cpa_e,
'CPA / FB'   : m_ch_cpa_fb,
'CPA / PUSH' : m_ch_cpa_p,
'EMAIL'      : m_ch_e,
'ETC'        : m_ch_etc,
'FB'         : m_ch_fb,
'PUSH'       : m_ch_p,
}
ddi = {
'CALLCENTER PROMO' : m_d_c,
'EMAIL PROMO'      : m_d_e,
'EMAIL UTM'        : m_d_eu,
'FB PROMO'         : m_d_fb,
'PUSH PROMO'       : m_d_p,
'REMOTE PROMO'     : m_d_r,
'PICODI PROMO'     : m_d_pic,
'FIX'              : m_d_fix,
'FULL PRICE'       : m_d_full,
}

tb_ch = pd_df(index = vch)

for ch, m_ch in dch.items():
 for di, m_di in ddi.items():
  tb_ch.loc[ch, di] = np.sum(m_ch & m_di)

vhosts = l.host_name[~l.host_name.duplicated() & l.host_name.notna()]
tb_hosts = pd_df(index = vhosts)
for host in vhosts:
 tb_hosts.loc[host, '#'] = np.sum(l.host_name == host)
tb_hosts = tb_hosts.sort_index(ascending = true)

# CPA, promo, base_ref   ##############################################################################################
mask_cpa_promo         = (l.cpa == 1) & (l.promo_code != '')
mask_ch_e_fb_push      = ((l.channel == 'CPA / EMAIL') | (l.channel == 'CPA / FB') | (l.channel == 'CPA / PUSH'))
df = l[mask_cpa_promo & mask_ch_e_fb_push].copy()
df['base_ref'] = np.nan
print(f'# has promo & CPA & EMAIL & FB & PUSH = {df_len(df)}')

re_baseref  = re.compile(r'((?:http://|https://)?.+?(?:/|$))')

df['app_base_ref']              = np.nan
df.app_base_ref                 = df.app_ref.str.extract(re_baseref, expand = false)
df = df[['app_base_ref','utm_source','promo_code','discount','channel']]
df = df.reset_index(drop = true)
df.discount = df.discount.notna()
df['promo_typ'] = np.nan
mask_mail   = df.utm_source.str.contains(r'esputnik-promo|creditup|email')
mask_icallc = df.promo_code.str.contains(r'^(?:f|r)\d{8}$', na = false)
mask_rcallc = df.promo_code.str.contains(r'^(?:\d{6})|(?:r\d{4})$', na = false)
mask_typ_fb    = df.utm_source.str.contains(r'fb|facebook') | (df.channel == 'FB') | (df.channel == 'CPA / FB')
mask_typ_push  = df.utm_source.str.contains(r'push') | (df.channel == 'PUSH') | (df.channel == 'CPA / PUSH')
mask_typ_email = mask_icallc | mask_rcallc | mask_mail | (df.channel == 'CPA / EMAIL') | (df.channel == 'EMAIL')
df.loc[mask_typ_email, 'promo_typ'] = 'EMAIL'
df.loc[mask_typ_push,  'promo_typ'] = 'PUSH'
df.loc[mask_typ_fb,    'promo_typ'] = 'FB'
df = df[['app_base_ref','utm_source','promo_code','discount','promo_typ']]
# #####################################################################################################################
save_e('sales_rep', {'data' : l, 'sales_ch' : tb_ch, 'sales_host' : tb_hosts, 'cpa_with_promos_ref' : df}, 
       need_date = false, need_index = true)