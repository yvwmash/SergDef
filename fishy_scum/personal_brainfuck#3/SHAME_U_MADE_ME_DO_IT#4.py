from inc import *
import inspect

# SHAME
#
#

def perror_exit(e_code = -1):
 print(' * line: ',inspect.currentframe().f_back.f_lineno)
 exit(e_code)

arg0   = 0
f_info = 0
if argc == 0:
 print('usage: python calls.py <-i>\n  -i   information only')
 sys.exit(0)
if argc == 2:
 arg0 = argv[1]
if arg0 not in (0, '-i'):
 print('usage: python calls.py <-i>\n  -i   information only')
 sys.exit(0)

if arg0 == '-i':
 f_info = 1

# date SQL params
DAYS_LIMIT  = 4
YEAR        = 2019
MONTH       = 11
LAST_DAY = last_day(YEAR, MONTH)
max_date = date(year = YEAR, month = MONTH,  day = LAST_DAY)
min_date = date(year = YEAR, month = MONTH,  day = 1)

#pd.set_option('display.max_columns', None)

# OPERATORS
# для отчета не нужны, можно считать с ними,
ext_oprt = [1013, 1015, 1029, 1031, 1046]
fic_oprt = [1091, 1092, 1093, 1094, 1095, 1096, 1097, 1098, 1099]

#september
#~ int_oprt = [1011,	1017,	1019,	1021,	1022,	1025,	1026,	1027,	1036,	1037,	1039,	1041,	1042,	1043,	1044]
#~ rem_oprt = [2017,	2024]

#october
#~ int_oprt = [1011,	1017,	1019,	1021,	1022,	1025,	1026,	1027,	1036,	1039,	1037,	1040,	1041,	1042,	1043,	1044,]
#~ rem_oprt = [2001,	2017,	2024,	2039]

# november
# внутрений отдел + удаленщики
int_oprt = [1011,	1017,	1019,	1021,	1022,	1025,	1026,	1027,	1037,	1040,	1041,	1042,	1043,	1044]
rem_oprt = [2001,	2017,	2024,	2025,	2039]

int_oprt = [str(i) for i in int_oprt]
ext_oprt = [str(i) for i in ext_oprt]
rem_oprt = [str(i) for i in rem_oprt]
fic_oprt = [str(i) for i in fic_oprt]

# requests
rq_ast = read_f('asterisk.sql')
rq_loa = read_f('loans.sql')
rq_ast = rq_ast.replace('dt_call_min',"'" + str(min_date) + "'")
rq_ast = rq_ast.replace('dt_call_max',"'" + str(max_date) + "'")

#calls from asterisk #############################################################################################################################################################################
status, mq_conn = q_connect('asterisk')
if status < 0:
 perror_exit()
print('asterisk query')
nrows, calls = q_fetch(mq_conn, rq_ast)
q_close(mq_conn)

print('process calls')
st = time()

calls.phone          = calls.phone.str.replace(r'.*anonymous.*', '0')
calls.operator       = calls.operator.str.replace(r'.*?/(\d+).*', r'\1')
calls                = calls[calls.operator.isin(int_oprt + rem_oprt + ext_oprt + fic_oprt)]
calls['call_center']                                    = 'CALL-CENTER'
calls.loc[calls.operator.isin(rem_oprt), 'call_center'] = 'REMOTE'
calls                                                   = calls[calls.res != 'FAILED']

df_conv(calls,{
'calldate' : 'datetime',
})

calls = calls.set_index('phone')
print('# call records = ', calls.shape[0], '\n')

#apps mysql ###########################################################################################################
st = time()
status, mq_conn = q_connect('front')
if status < 0:
 perror_exit()

min_pdate = date(min_date.year, min_date.month, min_date.day)
min_date  = date(max_date.year, max_date.month, 1)
rq_loa = rq_loa.replace('dt_loan_min',  "'" + str(min_date) + "'")
rq_loa = rq_loa.replace('dt_ploan_min', "'" + str(min_pdate) + "'")
rq_loa = rq_loa.replace('dt_loan_max',  "'" + str(max_date) + "'")

print('apps query')
nrows, apps = q_fetch(mq_conn, rq_loa)
q_close(mq_conn)

print('process apps')
st = time()
df_conv(apps,{
'created_at'        : 'datetime',
'prev_loan'         : 'datetime',
'actual_this_month' : 'int',
})
apps['call_center'] = 'nocallcenter'
apps['operator']    = 'nooperator'

apps.promo_code.fillna('nopromo', inplace = true)
mask_i_ops = apps.promo_code.str.contains(r'^(?:(?:R|F)\d{8})$')
mask_r_ops = apps.promo_code.str.contains(r'^\d{2}20\d{2}$')
apps.loc[mask_i_ops, 'operator'] = '10' + apps.loc[mask_i_ops, 'promo_code'].str.extract(r'^(?:R|F)\d{6}(\d{2})$', expand = false)
apps.loc[mask_r_ops, 'operator'] =        apps.loc[mask_r_ops, 'promo_code'].str.extract(r'^\d{2}(\d{4})$',        expand = false)
apps.loc[mask_i_ops, 'call_center'] = 'CALL-CENTER'
apps.loc[mask_r_ops, 'call_center'] = 'REMOTE'
apps = apps.set_index('phone')
print('# app records = ', apps.shape[0])

# actual apps = loans
print('join and grouping')
loans = apps[(apps.actual_this_month == 1)].drop(columns = ['promo_code', 'actual_this_month'])
# has/no promo
hp_loans = loans.loc[loans.operator != 'nooperator'].copy()
#print('hp src loans = ', hp_loans.shape[0])
np_loans = loans.loc[loans.operator == 'nooperator'].copy()
np_loans.drop(columns = ['call_center','operator'], inplace = True)
np_loans = np_loans.join(calls, how = 'inner')
#print('np join calls loans = ', np_loans.shape[0])
np_loans['tdiff'] = np_loans.created_at - np_loans.calldate
np_loans = np_loans[(np_loans.tdiff.dt.days >= 0) & (np_loans.tdiff.dt.days <= DAYS_LIMIT)]
#print('np loans tm diff = ', np_loans.shape[0])
np_loans = np_loans[np_loans.groupby('created_at')['tdiff'].rank(method='dense') == 1]
#print('np loans rank = ', np_loans.shape[0])
np_loans = np_loans.drop(columns = ['tdiff','calldate', 'res'])
hp_loans['call_type'] = 'is_loan'
np_loans['call_type'] = 'is_loan'
loans = pd.concat([hp_loans, np_loans], sort = true)
loans['htyp'] = 'cold'
loans.loc[(loans.created_at - loans.prev_loan).dt.days < 15, 'htyp'] = 'hot'
#loans.loc[(loans.created_at == loans.prev_loan), 'htyp'] = 'cold'
apps['htyp'] = 'cold'
apps.loc[(apps.created_at.dt.month - apps.prev_loan.dt.month).isin([0,1]), 'htyp'] = 'hot'

print('process loans & calls')
calls['htyp'] = 'cold'
calls.loc[calls.index.isin(apps[apps.htyp == 'hot'].index), 'htyp'] = 'hot'

vcalls = calls[~calls.operator.isin(int_oprt + rem_oprt)]
vloans = loans[~loans.operator.isin(int_oprt + rem_oprt)]

loans.reset_index(drop = true, inplace = true)
calls.reset_index(drop = true, inplace = true)
loans = loans[(loans.created_at.dt.date >= min_date) & (loans.created_at.dt.date <= max_date)]
loans.loc[:, 'dayy'] = loans.created_at.dt.day
calls = calls[((calls.calldate.dt.date >= min_date) & (calls.calldate.dt.date <= max_date)) | (calls.calldate.isna())]
calls.loc[:, 'dayy'] = calls.calldate.dt.day
print('# loans = ', loans.shape[0])
print('# calls = ', calls.shape[0])
print('li:', loans.index[0])
print('ci:', loans.index[0])

#######################################################################################################################################

st = time()
print('------------------------ info ------------------------ \n')

if vcalls.shape[0] > 0:
 print('\nvcalls = ', vcalls.shape[0])
 print(vcalls)
if vloans.shape[0] > 0:
 print('\nvloans = ', vloans.shape[0])
 print(vloans)
print('\n')

print('# loans : ', loans.shape[0])
print('# calls : ', calls.shape[0])

il = loans[loans.operator.isin(int_oprt + ext_oprt + fic_oprt)]
rl = loans[loans.operator.isin(rem_oprt)]
ic = calls[calls.operator.isin(int_oprt + ext_oprt + fic_oprt)]
rc = calls[calls.operator.isin(rem_oprt)]
# loans stats
ihl = il[il.htyp == 'hot']
icl = il[il.htyp == 'cold']
rhl = rl[rl.htyp == 'hot']
rcl = rl[rl.htyp == 'cold']
# calls stats
ihc = ic[ic.htyp == 'hot']
icc = ic[ic.htyp == 'cold']
rhc = rc[rc.htyp == 'hot']
rcc = rc[rc.htyp == 'cold']

# p loans
print('*  *  * loans *  *  *')
print('# ic      loans = ', il.shape[0])
print('# rc      loans = ', rl.shape[0])
print('# ic      calls = ', ic.shape[0])
print('# rc      calls = ', rc.shape[0])
nihc = ihc.shape[0]
nicc = icc.shape[0]
nrhc = rhc.shape[0]
nrcc = rcc.shape[0]
print('* ic hot  -> #loans = ', str(ihl.shape[0]).ljust(10), '  #calls = ', str(ihc.shape[0]).ljust(10), '  conv : ', str(round(ihl.shape[0] / nihc, 3)).ljust(10) if nihc else 0.0 )
print('# ic cold -> #loans = ', str(icl.shape[0]).ljust(10), '  #calls = ', str(icc.shape[0]).ljust(10), '  conv : ', str(round(icl.shape[0] / nicc, 3)).ljust(10) if nicc else 0.0 )
print('# rc hot  -> #loans = ', str(rhl.shape[0]).ljust(10), '  #calls = ', str(rhc.shape[0]).ljust(10), '  conv : ', str(round(rhl.shape[0] / nrhc, 3)).ljust(10) if nrhc else 0.0 )
print('# rc cold -> #loans = ', str(rcl.shape[0]).ljust(10), '  #calls = ', str(rcc.shape[0]).ljust(10), '  conv : ', str(round(rcl.shape[0] / nrcc, 3)).ljust(10) if nrcc else 0.0 )

print('# loans this month = ', apps[apps.actual_this_month == 1].shape[0])
print('# loans callcenter this month = ', loans.shape[0])

if f_info:
 sys.exit(0)

loans['typ'] = 'loan'
calls['typ'] = 'call'
loans['calldate']   = none
calls['created_at'] = none
loans['res']        = none
calls['prev_loan']  = none

callc_db = pd.concat([loans, calls], sort = true)

#######################################################################################################################################

# operator logic
# перетасовки тут(ушли, пришли, звонили под другим оператором)
callc_db.loc[:,'operator'] = callc_db.operator.str.replace('1005','1021')
callc_db.loc[:,'operator'] = callc_db.operator.str.replace('1013','1025')
callc_db.loc[:,'operator'] = callc_db.operator.str.replace('1015','1017')
callc_db.loc[:,'operator'] = callc_db.operator.str.replace('1024','1025')
callc_db.loc[:,'operator'] = callc_db.operator.str.replace('1029','1025')
callc_db.loc[:,'operator'] = callc_db.operator.str.replace('1031','1017')
callc_db.loc[:,'operator'] = callc_db.operator.str.replace('1046','1025')
callc_db.loc[:,'operator'] = callc_db.operator.str.replace('1062','1025')
callc_db.loc[:,'operator'] = callc_db.operator.str.replace('1072','1025')
callc_db.loc[:,'operator'] = callc_db.operator.str.replace('1091','1021')
callc_db.loc[:,'operator'] = callc_db.operator.str.replace('1092','1021')
callc_db.loc[:,'operator'] = callc_db.operator.str.replace('1093','1021')
callc_db.loc[:,'operator'] = callc_db.operator.str.replace('1094','1021')
callc_db.loc[:,'operator'] = callc_db.operator.str.replace('1095','1021')
callc_db.loc[:,'operator'] = callc_db.operator.str.replace('1096','1026')
callc_db.loc[:,'operator'] = callc_db.operator.str.replace('1097','1026')
callc_db.loc[:,'operator'] = callc_db.operator.str.replace('1098','1026')
callc_db.loc[:,'operator'] = callc_db.operator.str.replace('1099','1026')
callc_db.loc[:,'operator'] = callc_db.operator.str.replace('1038','1037')

#######################################################################################################################################

df = callc_db[['call_type','dayy','htyp','operator','typ','res']].copy()
df_conv(df, {
'call_type' : 'str',
'dayy'      : 'int',
'htyp'      : 'str',
'operator'  : 'int',
'typ'       : 'str',
'res'       : 'str',
})

i_ops = [int(i) for i in int_oprt]
ext_oprt = [int(i) for i in ext_oprt]
r_ops = [int(i) for i in rem_oprt]
fic_oprt = [int(i) for i in fic_oprt]

mask_call   = (df.typ       == 'call')
mask_loan   = (df.typ       == 'loan')
mask_call_o = (df.call_type == 'OUTGOING')
mask_call_i = (df.call_type == 'INCOMING')
mask_hot    = (df.htyp      == 'hot')
mask_cold   = (df.htyp      == 'cold')
mask_na     = (df.res       == 'NO ANSWER')
mask_a      = (df.res       == 'ANSWERED')
mask_b      = (df.res       == 'BUSY')

tb_ilc = pd_df(index = i_ops)
tb_ico = pd_df(index = i_ops)
tb_ici = pd_df(index = i_ops)
tb_rl  = pd_df(index = r_ops)
tb_rc  = pd_df(index = r_ops)
n      = last_day(min_date.year, min_date.month) + 1

for di in range(1,n):
 for op in i_ops:
  sday = str(di)
  h_call = 'call_hot_day_'  + sday
  c_call = 'call_cold_day_' + sday
  h_loan = 'loan_hot_day_'  + sday
  c_loan = 'loan_cold_day_' + sday
  h_conv = 'conv_hot_day_'  + sday
  c_conv = 'conv_cold_day_' + sday
  tb_ilc.loc[op, h_call] = np.sum((df.operator == op) & (df.dayy == di) & mask_call & mask_hot  & mask_call_o)
  tb_ilc.loc[op, c_call] = np.sum((df.operator == op) & (df.dayy == di) & mask_call & mask_cold & mask_call_o)
  tb_ilc.loc[op, h_loan] = np.sum((df.operator == op) & (df.dayy == di) & mask_loan & mask_hot)
  tb_ilc.loc[op, c_loan] = np.sum((df.operator == op) & (df.dayy == di) & mask_loan & mask_cold)
  tb_ilc.loc[op, h_conv] = tb_ilc.loc[op, h_loan]  / tb_ilc.loc[op, h_call]
  tb_ilc.loc[op, c_conv] = tb_ilc.loc[op, c_loan]  / tb_ilc.loc[op, c_call]
tb_ilc = tb_ilc.replace([np.inf, -np.inf], 0)

for di in range(1,n):
 for op in i_ops:
  sday = str(di)
  a_call  = 'call_a_day_'  + sday
  na_call = 'call_na_day_' + sday
  b_call  = 'call_b_day_'  + sday
  tb_ico.loc[op, a_call]  = np.sum((df.operator == op) & (df.dayy == di) & mask_call & mask_call_o & mask_a)
  tb_ico.loc[op, b_call]  = np.sum((df.operator == op) & (df.dayy == di) & mask_call & mask_call_o &mask_b)
  tb_ico.loc[op, na_call] = np.sum((df.operator == op) & (df.dayy == di) & mask_call & mask_call_o &mask_na)
tb_ico = tb_ico.replace([np.inf, -np.inf], 0)

for di in range(1,n):
 for op in i_ops:
  sday = str(di)
  a_call  = 'call_a_day_'  + sday
  na_call = 'call_na_day_' + sday
  b_call  = 'call_b_day_'  + sday
  tb_ici.loc[op, a_call]  = np.sum((df.operator == op) & (df.dayy == di) & mask_call & mask_call_i & mask_a)
  tb_ici.loc[op, b_call]  = np.sum((df.operator == op) & (df.dayy == di) & mask_call & mask_call_i & mask_b)
  tb_ici.loc[op, na_call] = np.sum((df.operator == op) & (df.dayy == di) & mask_call & mask_call_i & mask_na)
tb_ici = tb_ici.replace([np.inf, -np.inf], 0)

for di in range(1,n):
 for op in r_ops:
  sday = str(di)
  a_call  = 'call_a_day_'  + sday
  na_call = 'call_na_day_' + sday
  b_call  = 'call_b_day_'  + sday
  tb_rc.loc[op, a_call]  = np.sum((df.operator == op) & (df.dayy == di) & mask_call & mask_call_o & mask_a)
  tb_rc.loc[op, b_call]  = np.sum((df.operator == op) & (df.dayy == di) & mask_call & mask_call_o & mask_b)
  tb_rc.loc[op, na_call] = np.sum((df.operator == op) & (df.dayy == di) & mask_call & mask_call_o & mask_na)
tb_rc = tb_rc.replace([np.inf, -np.inf], 0)

for di in range(1,n):
 for op in r_ops:
  sday = str(di)
  tb_rl.loc[op, sday]  = np.sum((df.operator == op) & (df.dayy == di) & mask_loan)
tb_rl = tb_rl.replace([np.inf, -np.inf], 0)

# ############################################################################################################################
fn = save_e('callc_rep', {'tb_ilc':tb_ilc,'tb_ico':tb_ico,'tb_ici':tb_ici,'tb_rc':tb_rc,'tb_rl':tb_rl},
       need_date = false, need_index = true
)
