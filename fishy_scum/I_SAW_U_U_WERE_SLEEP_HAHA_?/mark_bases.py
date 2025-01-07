# -*- coding: utf-8 -*-

# Ежедневно, с утра для Романа
# 
# 

from inc import *
import inspect

def perror_exit(e_code = -1):
 print(' * line: ',inspect.currentframe().f_back.f_lineno)
 exit(e_code)

if argc < 1 or argc > 2:
 print('usage: python mark_bases.py')
 exit(0)

# black_list ###

status, mq_conn = q_connect('decision')
if status < 0:
 perror_exit()

nrows, exc = q_fetch(mq_conn, read_f('../qblack_list.sql'))
q_close(mq_conn)

exc.user_id = pd.to_numeric(exc.user_id)
exc = exc.iloc[:,0].to_list()
print('#exclude = ', len(exc))

# queries ###

rq = read_f('qmark_bases.sql')
r  = re.match(r'([^;]+;)([^;]+;)([^;]+;)', rq)
rq_c = r.group(1)
rq_3 = r.group(2)
rq_o = r.group(3)

status, mq_conn = q_connect('front')
if status < 0:
 perror_exit()

nrows, closed           = q_fetch(mq_conn, rq_c)
nrows, closed_in_3_days = q_fetch(mq_conn, rq_3)
nrows, open_loans       = q_fetch(mq_conn, rq_o)
q_close(mq_conn)

# process ###

df_conv(closed,{
'id'                    : 'int',
'overdue_days_max'      : 'int',
'count_loans'           : 'int',
'daysago'               : 'int',
'was_rejected'          : 'int',
'closed_at'             : 'date',
'date(us.activated_at)' : 'date',
'first_credit'          : 'date',
})

print('#closed = ', df_len(closed))
cmp = ~closed.iloc[:,0].isin(exc)
closed = closed[cmp]

df_conv(closed_in_3_days,{
'u_id'                     : 'int',
'app_id'                   : 'int',
'status_id'                : 'int',
'loan_days'                : 'int',
'overdue_days'             : 'int',
'prolongation_total_days'  : 'int',
'activated_at'             : 'date',
'applied_at'               : 'date',
'payment_date'             : 'date',
})

print('#closed_in_3_days = ', df_len(closed_in_3_days))
cmp = ~closed_in_3_days.iloc[:,0].isin(exc)
closed_in_3_days = closed_in_3_days[cmp]

df_conv(open_loans,{
'user_id'             : 'int',
'min_app_date'        : 'date',
'max_app_date'        : 'date',
'nloans'              : 'int',
'loan_overdues'       : 'int',
'is_overduer'         : 'int',
'ndays_in_credits'    : 'int',
'overdue_days_sum'    : 'int',
'activated_at'        : 'date',
})

print('#open = ', df_len(open_loans))
cmp = ~open_loans.iloc[:,0].isin(exc)
open_loans = open_loans[cmp]

print('#closed minus list           = ', df_len(closed))
print('#closed_in_3_days minus list = ', df_len(closed_in_3_days))
print('#open_loans minus list       = ', df_len(open_loans))

# save ###########################################################################################################################################

vdf = {'с закрытыми кредитами ': closed, 
       'закроется через 3 дня' : closed_in_3_days, 
       'с открытыми кредитами' : open_loans}
fn = save_e('mark_',vdf, 1, 0)

send_mail('analytic4@creditup.com.ua',
          ['Валентин Игоревич Лазепка <lazepkav@creditup.com.ua>', 'Роман Кузема <kuzema@creditup.com.ua>'],
          'маркетинг',
          '',
          [fn]
         )
