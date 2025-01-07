# -*- coding: utf-8 -*-

# MAIN за день по 1С
# на вход: <gsheet.xlsx> <1С отчет монитор деятельности> <1C отчет срезv2 по групам>
# 

from inc import *

pd.options.display.max_rows = 1000

if argc < 4:
 print('usage: python mcollect_1.py <google sheet> <монитор> <сборы> <-i|-b>')
 sys.exit(0)

fi  = 0
fg  = argv[1]
fm  = argv[2]
fc  = argv[3]
if argc > 4:
 fs = argv[4]
if argc == 6:
 fi = argv[5]

dg = pd.read_excel(fg, encoding = 'utf-8', header = None, index_col=0).fillna(0)
dc = pd.read_excel(fc, encoding = 'utf-8', index_col=0, skiprows = 6).fillna(0)
dc = dc.iloc[:-1]
dc.columns = ['###','#','body','%','total']
dm = pd.read_excel(fm, encoding = 'utf-8', index_col=0, skiprows = 7).fillna(0)
if argc > 4:
 ds = pd.read_excel(fs, encoding = 'utf-8', skiprows = 5).fillna(0)
 ds.columns = [re.sub(r'\n','',x).strip() for x in ds.columns.values]
 ds = ds.loc[:, ['Задолженность по телу','Кол-во дней просрочки']].iloc[:-1]
 ds.loc[:, 'Кол-во дней просрочки'] = c_conv(ds['Кол-во дней просрочки'], 'int')
 ds.loc[:, 'Задолженность по телу'] = c_conv(ds['Задолженность по телу'], 'float')
 s_novd   = 0
 s_sovd_b = 0
 s_nstd   = 0
 s_sstd_b = 0

#drop empty(join cell result) column
dc = dc.drop(columns='###')

gidx = [v.strip().lower() for v in dg.index.values]
cidx = [v.strip().lower() for v in dc.index.values]
gidx = [re.sub(r'^((?:\w+\s*){1,4}).*', r'\1', v).strip() for v in gidx]
gidx = [re.sub(r'^оператор (r.*)', r'\1', v) for v in gidx]
gidx = [re.sub(r'^оператор 45$', r'operator45', v) for v in gidx]
cidx = [re.sub(r'^((?:\w+\s*){1,4}).*', r'\1', v).strip() for v in cidx]

gidx = [re.sub(r'^4101_села_пиранья', '4101_киев_вгз1', v) for v in gidx]
#~ gidx = [re.sub(r'^4102_села_пиранья', '4102_киев_вгз2', v) for v in gidx]
#~ gidx = [re.sub(r'^4103_села_пиранья', '4103_киев_вг33', v) for v in gidx]
gidx = [re.sub(r'^4039_села_пиранья', '4039_киев_вг3', v) for v in gidx]
gidx = [re.sub(r'^4037_села_пиранья', '4037_киев_вг1', v) for v in gidx]
gidx = [re.sub(r'^Lawyer Нотариус Написи', 'lawyer_нотариус_написи', v) for v in gidx]
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

has_dups = dg.index.duplicated()
if has_dups.any():
 print('google sheet df has duplicates')
 print(dg[has_dups])
 sys.exit(0)

# new/rep
nnew  = dm.iloc[0, 0]
nrep  = dm.iloc[1, 0]
nlnew = dm.iloc[0, 3]
nlrep = dm.iloc[1, 3]
slnew = dm.iloc[0, 4]
slrep = dm.iloc[1, 4]

# collection
# std
if 'вовремя' not in dc.index:
 dc_std = pd.DataFrame(index = ['вовремя'], columns = ['#','body','%','total'], data = [[0,0,0,0]], dtype = float)
else:
 dc_std = dc.loc['вовремя':'просрочено'].iloc[:-1]
 cidx = dc_std.index.duplicated()
 dc_std = dc_std[~cidx]
nnstd     = dc_std.loc['вовремя', '#']
nstd_body = dc_std.loc['вовремя', 'body']
nstd_perc = dc_std.loc['вовремя', '%']
nstd_sum  = dc_std.loc['вовремя', 'total']

# ovd
dc_ovd = dc.loc['просрочено':]
cidx = dc_ovd.index.duplicated()
dc_ovd = dc_ovd[~cidx]
nnovd     = dc_ovd.loc['просрочено', '#']
novd_body = dc_ovd.loc['просрочено', 'body']
novd_perc = dc_ovd.loc['просрочено', '%']
novd_sum  = dc_ovd.loc['просрочено', 'total']
dc_ovd = dc_ovd.iloc[1:]

print('1c: ')
print('# std   = ', nnstd)
print('# ovd   = ', nnovd)
print('# std b = ', nstd_body)
print('# std % = ', nstd_perc)
print('# std ∑ = ', nstd_sum)

print('# payments = ', nnstd + nnovd)
print('# ovd b    = ', novd_body)
print('# ovd %    = ', novd_perc)
print('# ovd ∑    = ', novd_sum)
print('\n*** *** ***\n')

if fi == '-i':
 sys.exit(0)

j = pd.DataFrame(index = dg.index.insert(0, 'start'))
j = j.join(dc_ovd, how = 'left')
j = j[['total','body','%']]

vnms = ['start', 'итого soft1','итого soft2','итого middle','итого hard','итого коллекторские компании',
        'неопределенные','operator13','legal', 'стандартная реструктуризация','итого отдел реструктуризации',
        'итого региональные менеджеры']

vcmp = {'итого soft1':0,'итого soft2':0,'итого middle':0,'итого hard':0,'итого коллекторские компании':0,
        'неопределенные':0,'legal':0,'стандартная реструктуризация':0,
        'итого отдел реструктуризации':0,'итого региональные менеджеры':0}
vb = {'итого soft1':0,'итого soft2':0,'итого middle':0,'итого hard':0,'итого коллекторские компании':0,
        'неопределенные':0,'legal':0,'стандартная реструктуризация':0,
        'итого отдел реструктуризации':0,'итого региональные менеджеры':0}
vp = {'итого soft1':0,'итого soft2':0,'итого middle':0,'итого hard':0,'итого коллекторские компании':0,
        'неопределенные':0,'legal':0,'стандартная реструктуризация':0,
        'итого отдел реструктуризации':0,'итого региональные менеджеры':0}
single = ['неопределенные', 'стандартная реструктуризация', 'operator13']

for i in range(0, len(vnms) - 1):
 si = vnms[i]
 ei = vnms[i + 1]
 sd = ei
 df = j[si:ei].iloc[1:]
 if ei not in single:
  df = df.iloc[:-1]
 if df.shape[0] != 0:
  t_sum = df['total'].sum()
  b_sum = df['body'].sum()
  p_sum = df['%'].sum()
  print('%-34s : %-12.2f' % (sd, t_sum))
  vcmp[sd] = t_sum
  vb[sd] = b_sum
  vp[sd] = p_sum
j.drop(labels = 'start', inplace = true)

print('∑ 1c ovd = %.2f' % novd_sum)
print('∑ py ovd = %.2f' % sum(vcmp.values()))

comp_ni = ~dc_ovd.index.isin(j.index)
if comp_ni.any():
 print('!!! missing rows in result dataframe:')
 print(dc_ovd[comp_ni])
 sys.exit(0)

# slice
if argc > 4:
 mask_ovd = ds.loc[:, 'Кол-во дней просрочки'] > 0
 mask_std = (ds['Кол-во дней просрочки'] == 0) | (ds['Задолженность по телу'] == 0)
 s_novd   = ds.loc[mask_ovd].shape[0]
 s_sovd_b = ds.loc[mask_ovd, 'Задолженность по телу'].sum()
 s_nstd   = ds.loc[mask_std].shape[0]
 s_sstd_b = ds.loc[mask_std, 'Задолженность по телу'].sum()

# ######################################################################################################

wb = xl_wb()
ws_h = wb.active
ws_c = wb.create_sheet()
ws_h.title = 'показатели'
ws_c.title = 'сборы'
ws_m = wb.create_sheet()
ws_m.title = 'монитор деятельности'
ws_b = wb.create_sheet()
ws_b.title = 'бюджет'

if argc > 4:
 ws_s = wb.create_sheet()
 ws_s.title = 'срез'

 ws_s.cell(row = 1, column = 1).value = '# ovd'
 ws_s.cell(row = 2, column = 1).value = 'ovd_b'
 ws_s.cell(row = 3, column = 1).value = '# std'
 ws_s.cell(row = 4, column = 1).value = 'std_b'
 ws_s.cell(row = 1, column = 2).value = s_novd
 ws_s.cell(row = 2, column = 2).value = s_sovd_b
 ws_s.cell(row = 3, column = 2).value = s_nstd
 ws_s.cell(row = 4, column = 2).value = s_sstd_b

ws_h.cell(row = 1, column = 1).value = '# pays'
ws_h.cell(row = 2, column = 1).value = '# std body'
ws_h.cell(row = 3, column = 1).value = '# std %'
ws_h.cell(row = 4, column = 1).value = '# ovd body'
ws_h.cell(row = 5, column = 1).value = '# ovd %'
ws_h.cell(row = 1, column = 2).value = nnstd + nnovd # pays
ws_h.cell(row = 2, column = 2).value = nstd_body     # std body
ws_h.cell(row = 3, column = 2).value = nstd_perc     # std %
ws_h.cell(row = 4, column = 2).value = novd_body     # ovd body
ws_h.cell(row = 5, column = 2).value = novd_perc     # ovd %

ws_m.cell(row = 1, column = 1).value = '# new apps'
ws_m.cell(row = 2, column = 1).value = '# rep apps'
ws_m.cell(row = 3, column = 1).value = '# new loans'
ws_m.cell(row = 4, column = 1).value = '# rep loans'
ws_m.cell(row = 5, column = 1).value = 'sum new loans'
ws_m.cell(row = 6, column = 1).value = 'sum rep loans'
ws_m.cell(row = 1, column = 2).value = nnew  # new apps
ws_m.cell(row = 2, column = 2).value = nrep  # rep apps
ws_m.cell(row = 3, column = 2).value = nlnew # new loans
ws_m.cell(row = 4, column = 2).value = nlrep # rep loans
ws_m.cell(row = 5, column = 2).value = slnew # sum new loans
ws_m.cell(row = 6, column = 2).value = slrep # sum rep loans

ws_b.cell(row = 1, column = 1).value = '# new loans'
ws_b.cell(row = 2, column = 1).value = '# rep loans'
ws_b.cell(row = 3, column = 1).value = 'sum rep loans'
ws_b.cell(row = 4, column = 1).value = 'sum rep loans'
ws_b.cell(row = 1, column = 2).value = nlnew # new loans
ws_b.cell(row = 2, column = 2).value = nlrep # rep loans
ws_b.cell(row = 3, column = 2).value = slnew # sum rep loans
ws_b.cell(row = 4, column = 2).value = slrep # sum rep loans

ws_b.cell(row = 5, column = 1).value = '---'
ws_b.cell(row = 6, column = 1).value = 'COLLECT'
ws_b.cell(row = 7, column = 2).value = 'body'
ws_b.cell(row = 7, column = 3).value = '%'

ws_b.cell(row = 8,  column = 1).value = '-SOFT1'
ws_b.cell(row = 9,  column = 1).value = '-SOFT2'
ws_b.cell(row = 10, column = 1).value = '-MIDDLE'
ws_b.cell(row = 11, column = 1).value = '-региональные менеджеры'
ws_b.cell(row = 12, column = 1).value = '-коллекторские колл-центры'
ws_b.cell(row = 13, column = 1).value = '-реструктуризация'
ws_b.cell(row = 14, column = 1).value = '-legal'
ws_b.cell(row = 8,  column = 2).value = vb['итого soft1'] + vb['неопределенные']                                #-SOFT1'
ws_b.cell(row = 9,  column = 2).value = vb['итого soft2']                                                       #-SOFT2'
ws_b.cell(row = 10, column = 2).value = vb['итого middle']                                                      #-MIDDLE'
ws_b.cell(row = 11, column = 2).value = vb['итого региональные менеджеры'] + vb['итого hard']                   #-региональные менеджеры'
ws_b.cell(row = 12, column = 2).value = vb['итого коллекторские компании']                                      #-коллекторские колл-центры'
ws_b.cell(row = 13, column = 2).value = vb['стандартная реструктуризация'] + vb['итого отдел реструктуризации'] #-реструктуризация'
ws_b.cell(row = 14, column = 2).value = vb['legal']                                                             #-legal'
ws_b.cell(row = 8,  column = 3).value = vp['итого soft1'] + vp['неопределенные']                                #-SOFT1'
ws_b.cell(row = 9,  column = 3).value = vp['итого soft2']                                                       #-SOFT2'
ws_b.cell(row = 10, column = 3).value = vp['итого middle']                                                      #-MIDDLE'
ws_b.cell(row = 11, column = 3).value = vp['итого региональные менеджеры'] + vp['итого hard']                   #-региональные менеджеры'
ws_b.cell(row = 12, column = 3).value = vp['итого коллекторские компании']                                      #-коллекторские колл-центры'
ws_b.cell(row = 13, column = 3).value = vp['стандартная реструктуризация'] + vp['итого отдел реструктуризации'] #-реструктуризация'
ws_b.cell(row = 14, column = 3).value = vp['legal']                                                             #-legal'


h_green = xl_style(name='h_green')
h_green.font = xl_font(bold=True, size = 12)
h_green.fill = xl_fill(fill_type='solid', fgColor='9BBB59')
h_green.alignment = xl_align(horizontal = 'center')
h_grey = xl_style(name='h_grey')
h_grey.font = xl_font(bold = true, size = 12)
h_grey.fill = xl_fill(fill_type='solid', fgColor='778899')
h_c = xl_style(name='h_c')
h_c.alignment = xl_align(horizontal = 'center')

j.update(pd.DataFrame(data = vcmp.values(), index = vcmp.keys(), columns = ['total']))
j = j.reset_index()
for i in range(len(j)):
 ci = i + 1
 n = j.iloc[i,0]
 v = j.iloc[i,1]
 nc = ws_c.cell(row = ci, column = 1)
 vc = ws_c.cell(row = ci, column = 2)
 nc.value = n
 vc.value = v

for row in ws_c.rows:
 a = row[0]
 b = row[1]
 if a.value in vnms:
  a.style = h_grey
  b.style = h_c
 elif a.value not in (set(vnms) - set(single)):
  b.style = h_green

autosize_ws(ws_m)
autosize_ws(ws_c)
autosize_ws(ws_h)
autosize_ws(ws_b)
if argc > 4:
 autosize_ws(ws_s)

wb.save('/mnt/hdd/excel/from_scripts/collect_1_day.xlsx')
