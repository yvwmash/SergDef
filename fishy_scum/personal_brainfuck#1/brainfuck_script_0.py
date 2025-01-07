# -*- coding: utf-8 -*-

# Сравнение автоплате

from inc import *
import inspect

def perror_exit(e_code = -1):
 print(' * line: ',inspect.currentframe().f_back.f_lineno)
 exit(e_code)

if argc < 2:
 print('usage: python autopays.py <autopays>')
 sys.exit(0)

fn = argv[1]

autopays = pd.read_excel(fn, encoding = 'utf-8', index_col = none, skiprows = 1)
autopays = autopays.iloc[:-1]
autopays.columns = autopays.columns.str.strip()
autopays.columns = autopays.columns.str.replace(r'\s+',' ')
autopays = autopays[['Дата оплаты','Контрагент','Сумма тела','Сумма процентов','Сумма итого','Сотрудник']]
autopays.columns = ['dt', 'nm', 'body', 'ovd', 'total', 'op']

## excel
df_conv(autopays,{'dt' : 'date',
                  'nm' : 'str',
                  'body' : 'float',
                  'ovd' : 'float',
                  'total' : 'float',
                  'op' : 'str'
})
autopays.nm = autopays.nm.str.replace(r'(.*?)\.', r'\1')
autopays.nm = autopays.nm.str.strip()
autopays.nm = autopays.nm.str.lower()

## query
rq = read_f('autopays.sql')
min_date = date(year = 2019, month = 9, day = 1)
max_date = date(year = 2019, month = 9, day = 30)
rq = rq.replace('dt_min', "'" + str(min_date) + "'")
rq = rq.replace('dt_max', "'" + str(max_date) + "'")

print('query')
status, con = q_connect('front')
if status < 0:
 perror_exit()
nrows, qpays = q_fetch(con, rq)
q_close(con)
print('done query in : %f' % t1)

df_conv(qpays,{'uid'       : 'int',
                  'f_nm'     : 'str',
                  's_nm'     : 'str',
                  't_nm'     : 'str',
                  'paid'     : 'float',
                  'apps'     : 'str',
                  'inns'     : 'str'
})
qpays.f_nm = qpays.f_nm.str.lower()
qpays.s_nm = qpays.s_nm.str.lower()
qpays.t_nm = qpays.t_nm.str.lower()
qpays.f_nm = qpays.f_nm.str.replace(r'^$',' ')
qpays.s_nm = qpays.s_nm.str.replace(r'^$',' ')
qpays.t_nm = qpays.t_nm.str.replace(r'^$',' ')
qpays['fn'] = qpays.s_nm + ' ' + qpays.f_nm.str[0] + ' ' + qpays.t_nm.str[0]
qpays.fn = qpays.fn.str.replace(r'\s+', ' ')
qpays.fn = qpays.fn.str.strip()

## join
autopays = autopays.set_index('nm')
qpays    = qpays.set_index('fn')
j = df_join(autopays, qpays, how = 'left')
j.index.name = 'ФИО'

mask = j.uid.isna()
t = j[mask].copy()
j = j[~mask]

t = t.reset_index()
t['~'] = t['ФИО'].apply(lambda x : [process.extract(x, qpays.index, limit = 1)][0][0][0])
t = t.set_index('~')
t = t[['ФИО','dt','body','ovd','total','op']]
t = df_join(t, qpays, how = 'left')
t = t.reset_index(drop = true)

##################################################################################################################

vdf = {'autopays': j, '~' : t, 'mysql' : qpays}
fn = save_e('autopays',vdf, need_index = 0, need_date = 1)
