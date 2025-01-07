# -*- coding: utf-8 -*-

# 3 групы обзвона 1) /* NOT ACTIVE*/ 2) /*ACTIVE WITHOUT APPLICATION*/ 3) /* new - calceled */
#

from inc import *
import inspect

def perror_exit(e_code = -1):
 print(' * line: ',inspect.currentframe().f_back.f_lineno)
 exit(e_code)

if argc < 1 or argc > 2:
 print('usage: python callc_clist.py')
 sys.exit(0)

# black_list ###
status, mq_conn = q_connect('decision')
if status < 0:
 perror_exit()
nrows, exc = q_fetch(mq_conn, read_f('../qblack_list.sql'))
q_close(mq_conn)

exc.user_id = pd.to_numeric(exc.user_id)
exc = exc.iloc[:,0].to_list()
print('#exclude = ', len(exc))

# stop_list ###
stop = pd.read_excel('stop_list.xlsx', sep = ';', encoding = 'utf-8', dtype = str).fillna(0)
stop = stop.iloc[:,0].to_list()
print('#stop = ', len(stop))

exc = list(set(exc + stop))

# queries ###

rq_clist = read_f('callc_clist.sql')

max_date = date(year = 2019, month = 11,  day = 20) # с [четверга по четверг)
min_date = date(year = 2019, month = 11,  day = 14) #
rq_clist = rq_clist.replace('dt_call_min',"'" + str(min_date) + "'")
rq_clist = rq_clist.replace('dt_call_max',"'" + str(max_date) + "'")

status, mq_conn = q_connect('front')
if status < 0:
 perror_exit()
nrows, df = q_fetch(mq_conn, rq_clist)
q_close(mq_conn)

# process ###

nactive = df[df.typ == 'noa']
print('#nactive = ', nactive.shape[0])
cmp = ~nactive.iloc[:,0].isin(exc)
nactive = nactive[cmp]
nactive = nactive.drop(axis = 'columns', columns = 'typ')

woapp = df[df.typ == 'awo']
print('#woapp = ', woapp.shape[0])
cmp = ~woapp.iloc[:,0].isin(exc)
woapp = woapp[cmp]
woapp = woapp.drop(axis = 'columns', columns = 'typ')

new_canceled = df[df.typ == 'nc']
print('#new_canceled = ', new_canceled.shape[0])
cmp = ~new_canceled.iloc[:,0].isin(exc)
new_canceled = new_canceled[cmp]
new_canceled = new_canceled.drop(axis = 'columns', columns = 'typ')

print('#nactive minus list      = ', nactive.shape[0])
print('#woapp minus list        = ', woapp.shape[0])
print('#new_canceled minus list = ', new_canceled.shape[0])

# save ###########################################################################################################################################

vdf = {'не активные': nactive, 'активные без заявки': woapp, 'новые, отменены' : new_canceled}

nday = date.today().strftime('%d')
vdf = {'no_active '     + nday : nactive,
       'active_wo_app ' + nday : woapp,
       'new_cancelled ' + nday : new_canceled}
fn = save_e('callc_list', vdf, need_date = 0, need_index = 0)
