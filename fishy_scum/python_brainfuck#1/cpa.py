# -*- coding: utf-8 -*-

from inc import *
import inspect

def perror_exit(e_code = -1):
 print(' * line: ',inspect.currentframe().f_back.f_lineno)
 exit(e_code)

rq0 = read_f('cpa0.sql')
rq1 = read_f('cpa1.sql')

# date SQL params
YEAR     = 2019
MONTH    = 11
LAST_DAY = last_day(YEAR, MONTH)
max_date = date(year = YEAR, month = MONTH,  day = LAST_DAY)
min_date = date(year = YEAR, month = MONTH,  day = 1)

rq0 = rq0.replace('dt_min',"'" + str(min_date) + "'")
rq0 = rq0.replace('dt_max',"'" + str(max_date) + "'")
rq1 = rq1.replace('dt_min',"'" + str(min_date) + "'")
rq1 = rq1.replace('dt_max',"'" + str(max_date) + "'")

st = time()
status, mq_conn = q_connect('front')
if status < 0:
 perror_exit()
 
print('query')
nrows, df0 = q_fetch(mq_conn, rq0)
nrows, df1 = q_fetch(mq_conn, rq1)
q_close(mq_conn)
t0 = time() - st
print('done query in : %f' % t0)

df_conv(df0, 
       {'yearof'           : 'int',
        'monthof'          : 'int',
        'dateof'           : 'datetime',
        'napplications'    : 'int'
})
df_conv(df1, 
       {'created_at'       : 'datetime',
        'updated_at'       : 'datetime',
})

vdays = list(range(min_date.day, max_date.day + 1))
vadv  = ['admitad', 'doaffiliate', 'finline', 'leadgid', 'leads', 
         'linkprofit', 'loangate', 'primelead', 'sales_doubler']
tb_by_day = pd_df(index = vdays)
for n in vdays:
 for a in vadv:
  m_day = df0.dateof.dt.day == n
  m_adv = df0.provider      == a
  m_new = df0.user_type     == 'NEW'
  m_rep = df0.user_type     == 'REPEAT'
  tb_by_day.loc[n, a + '_new'] = df0[m_day & m_adv & m_new].napplications.sum()
  tb_by_day.loc[n, a + '_rep'] = df0[m_day & m_adv & m_rep].napplications.sum()
  tb_by_day.loc[n, a + '_sum'] = df0[m_day & m_adv].napplications.sum()

vsite = ['bestcredit', 'creditup']
tb_site = pd_df(index = vsite)
for s in vsite:
 m_site = df0.site_credit == s
 tb_site.loc[s, 'sum'] = df0[m_site].napplications.sum()

save_e('cpa_rep', {'выборка' : df0, 'все данные' : df1, 'by_day' : tb_by_day, 'by_site' : tb_site}, 
       need_date = false, need_index = true)