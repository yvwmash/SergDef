# -*- coding: utf-8 -*-

# MAIN за период(с начала месяца) по 1С
# с 10.00 запускать отчеты 1С
# на вход: <gsheet.xlsx> <1С отчет монитор деятельности> <1C отчет срезv2 по групам> <1C отчет срезv2 - автопогашение>
# пример: > python3 mcollect_n.py </gsheet.xlsx> <m.xls> <c.xls> <a.xls>
# на выходе ексель файл с листами для заполнения MAIN отчета

from inc import *
import inspect

if argc < 5:
 print('usage: python collect <google sheet> <монитор деятельности> <сборы> <автопогашение>')
 sys.exit(0)

fg  = argv[1]
fm  = argv[2]
fc  = argv[3]
fa  = argv[4]

dg = pd.read_excel(fg, encoding = 'utf-8', header = None, index_col=0).fillna(0)
dm = pd.read_excel(fm, encoding = 'utf-8', index_col=0, skiprows = 7).fillna(0)
dm['кво'].replace(' ', np.nan, inplace = true)
dm.dropna(subset=['кво'], inplace = true)
dm.index = dm.index.astype(str)
dc = pd.read_excel(fc, encoding = 'utf-8', index_col=0, skiprows = 6).fillna(0)
dc = dc.iloc[:-1]
dc.columns = ['###','#','body','%','total']

#drop empty(join cell result) column
dc = dc.drop(columns='###')

gidx = [v.strip().lower() for v in dg.index.values]
cidx = [v.strip().lower() for v in dc.index.values]
gidx = [re.sub(r'^((?:\w+\s*){1,4}).*', r'\1', v).strip() for v in gidx]
gidx = [re.sub(r'^оператор (r.*)', r'\1', v) for v in gidx]
gidx = [re.sub(r'^оператор 45$', r'operator45', v) for v in gidx]
cidx = [re.sub(r'^((?:\w+\s*){1,4}).*', r'\1', v).strip() for v in cidx]

gidx = [re.sub(r'^4101_села_пиранья', '4101_киев_вгз1', v) for v in gidx]
gidx = [re.sub(r'^4102_села_пиранья', '4102_киев_вгз2', v) for v in gidx] # 2019.09
gidx = [re.sub(r'^4103_села_пиранья', '4103_киев_вг33', v) for v in gidx] # 2019.09
gidx = [re.sub(r'^4039_села_пиранья', '4039_киев_вг3', v) for v in gidx]
gidx = [re.sub(r'^4037_села_пиранья', '4037_киев_вг1', v) for v in gidx]
gidx = [re.sub(r'^12_села_пиранья', 'operator12', v) for v in gidx]       # 2019.11
gidx = [re.sub(r'^lawyer нотариус написи', 'lawyer_нотариус_написи', v) for v in gidx]
gidx = [re.sub(r'^кредит экспресс украина', 'кредит экспресс украина 2', v) for v in gidx]
gidx = [re.sub(r'^итого вг', 'итого региональные менеджеры', v) for v in gidx]
gidx = [re.sub(r'^оператор13', 'operator13', v) for v in gidx]
cidx = [re.sub(r'^$', 'неопределенные', v).strip() for v in cidx]
cidx = [re.sub(r'^fraud$', 'operator13', v).strip() for v in cidx]
cidx = [re.sub(r'^standartrestruct$', 'стандартная реструктуризация', v) for v in cidx]
dc.index = cidx
dg.index = gidx
exc_dc_rgx = re.compile(r'^(?!hard$|soft(?:1|2)$|middle$|external_collection$|external_region$|restruct$)', re.I)
dc = dc.filter(regex=exc_dc_rgx, axis=0)
dc = dc.append(pd.Series(name='E'))

has_dups = dg.index.duplicated()
if has_dups.any():
 print('google sheet df has duplicates')
 print(dg[has_dups])
 sys.exit(0)

da = pd.read_excel(fa, encoding = 'utf-8', header = None, index_col = None, skiprows = 2, dtype = str).fillna(0)
da.columns = ['dt','nm','# agreement','body','%','total','op']
da = da[['dt','body','%','op']]
da = da.iloc[:-1]
da.op = da.op.str.strip()
da.op = da.op.str.lower()
da.op = da.op.str.replace(r'^$','неопределенные')
da.op = da.op.str.replace(r'^standartrestruct$','стандартная реструктуризация')
da.op = da.op.str.replace(r'^((?:\w+\s*){1,4}).*',r'\1')
da['body'] = c_conv(da['body'], 'float')
da['%']    = c_conv(da['%'],    'float')
gda = da.groupby(['dt'])

rda = pd.DataFrame(index = ['body','%'])
for k, v in gda:
 cday = re.sub(r'^(..)\...\...$',r'\1', k)
 r = pd.Series(data = [v['body'].sum(), v['%'].sum()], index = ['body','%'], dtype = float)
 rda[cday] = r

# монитор деятельности ##########################################################
dm.index = dm.index.str.replace(' ', '', regex = false)
dm.index = dm.index.str.replace(r'^....-..-(..$)', r'\1', regex = true)
dm.index = dm.index.str.replace(r'^0(.)$', r'\1', regex = true)
vd = dm.index[dm.index.str.contains(r'^\d')].to_list()

rdm = pd.DataFrame(columns = vd, index = ['# new apps','# rep apps', '# new issuance', '# rep issuance', 'sum new issuance', 'sum rep issuance'])

i = 0
n = len(vd)
while i < n:
 cday = vd[i]
 if i == n - 1:
  nday = 'ИТОГО:'
 else:
  nday = vd[i+1]
 df = dm[cday:nday].iloc[1:-1]
 rdm.loc['# new apps',cday]       = int(df.iloc[0,0])
 rdm.loc['# rep apps',cday]       = int(df.iloc[1,0])
 rdm.loc['# new issuance',cday]   = int(df.iloc[0,3])
 rdm.loc['# rep issuance',cday]   = int(df.iloc[1,3])
 rdm.loc['sum new issuance',cday] = float(df.iloc[0,4])
 rdm.loc['sum rep issuance',cday] = float(df.iloc[1,4])
 i = i + 1
##############################################################################

# collect ##########################################################
dc.index = dc.index.str.replace(r'^....-..-(..$)', r'\1', regex = true)
dc.index = dc.index.str.replace(r'^0(.)$', r'\1', regex = true)
vd = dc.index[dc.index.str.contains(r'^\d{1,2}$')].to_list()

rdc0 = pd.DataFrame(columns = vd, index = ['# payments','std body', 'std %', 'ovd body', 'ovd %'])
rdc1 = pd.DataFrame(columns = vd, index = dg.index)
rdc1.index.name = 'nm'
i = 0
n = len(vd)
while i < n:
 cday = vd[i]
 if i == n - 1:
  nday = 'E'
 else:
  nday = vd[i+1]
 df = dc[cday:nday].iloc[1:-1]
 if 'вовремя' not in dc.index:
  dc_std = pd.DataFrame(index = ['вовремя'], columns = ['#','body','%','total'], data = [[0,0,0,0]], dtype = float)
 else:
  dc_std = df.loc['вовремя':'просрочено'].iloc[:-1]
  cidx = dc_std.index.duplicated()
  dc_std = dc_std[~cidx]
 nnstd     = dc_std.loc['вовремя', '#']
 nstd_body = dc_std.loc['вовремя', 'body']
 nstd_perc = dc_std.loc['вовремя', '%']
 nstd_sum  = dc_std.loc['вовремя', 'total']
 dc_ovd = df.loc['просрочено':]
 cidx = dc_ovd.index.duplicated()
 dc_ovd = dc_ovd[~cidx]
 nnovd     = dc_ovd.loc['просрочено', '#']
 novd_body = dc_ovd.loc['просрочено', 'body']
 novd_perc = dc_ovd.loc['просрочено', '%']
 novd_sum  = dc_ovd.loc['просрочено', 'total']
 dc_ovd = dc_ovd.iloc[1:]
 rdc0.loc['# payments',cday] = int(nnstd + nnovd)
 rdc0.loc['std body',cday]   = float(nstd_body)
 rdc0.loc['std %',cday]      = float(nstd_perc)
 rdc0.loc['ovd body',cday]   = float(novd_body)
 rdc0.loc['ovd %',cday]      = float(novd_perc)

 j = pd.DataFrame(index = dg.index.insert(0, 'start'))
 j = j.join(dc_ovd, how = 'left')
 j = j[['total']]

 vnms = ['start', 'итого soft', 'итого soft1','итого soft2','итого middle','итого hard','итого коллекторские компании',
        'неопределенные','operator13','legal', 'стандартная реструктуризация','итого отдел реструктуризации',
        'итого региональные менеджеры']

 vcmp = {'итого soft1':0, 'итого soft1':0,'итого soft2':0,'итого middle':0,'итого hard':0,'итого коллекторские компании':0,
        'неопределенные':0,'legal':0,'стандартная реструктуризация':0,
        'итого отдел реструктуризации':0,'итого региональные менеджеры':0}
 vb = {'итого soft1':0,'итого soft1':0,'итого soft2':0,'итого middle':0,'итого hard':0,'итого коллекторские компании':0,
        'неопределенные':0,'legal':0,'стандартная реструктуризация':0,
        'итого отдел реструктуризации':0,'итого региональные менеджеры':0}
 vp = {'итого soft1':0,'итого soft1':0,'итого soft2':0,'итого middle':0,'итого hard':0,'итого коллекторские компании':0,
        'неопределенные':0,'legal':0,'стандартная реструктуризация':0,
        'итого отдел реструктуризации':0,'итого региональные менеджеры':0}
 single = ['неопределенные', 'стандартная реструктуризация', 'operator13']
 
 for k in range(0, len(vnms) - 1):
  si = vnms[k]
  ei = vnms[k + 1]
  sd = ei
  df = j[si:ei].iloc[1:]
  if ei not in single:
   df = df.iloc[:-1]
  if df.shape[0] != 0:
   t_sum = df['total'].sum()
   vcmp[sd] = t_sum

 j.drop(labels = 'start', inplace = true)
 j.update(pd.DataFrame(data = vcmp.values(), index = vcmp.keys(), columns = ['total']))
 j.rename(inplace = true, columns = {'total' : cday})
 j.index.name = 'nm'
 j.update(pd.DataFrame(data = vcmp.values(), index = vcmp.keys(), columns = [cday]))
 rdc1.update(j)

 comp_ni = ~dc_ovd.index.isin(j.index)
 if comp_ni.any():
  print('!!! missing rows in result dataframe:')
  print(dc_ovd[comp_ni])
  sys.exit(0)

 i = i + 1

##############################################################################

## autopayments

##############################################################################

vdf = {'монитор деятельности' : rdm, 'показатели' : rdc0, 'сборы' : rdc1, 'автопогашение' : rda}
fn = save_e('collect_n_days', vdf, 
       need_date = false, need_index = true)


