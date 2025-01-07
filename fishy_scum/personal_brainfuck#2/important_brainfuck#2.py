# -*- coding: utf-8 -*-

# Портфель для Вадима
# По спискам e-mail, сводит со срезом, агрегирует сумы.

from inc import *
import inspect

if argc > 1:
 print('usage python3 esputnik.py')
 exit()

print(' + read slice')
df_s = pd.read_csv('/mnt/hdd/db_io/1C/201911/s_20.csv',
                   dtype      = str, 
                   skiprows   = 5,
                   skipfooter = 1,
                   sep        = '\t',
                   quotechar  = '"', 
                   encoding   = 'utf-8',
                   engine     = 'python'
)

df_s.columns = df_s.columns.str.strip()
df_s.columns = df_s.columns.str.replace(r'\s+',' ')

df_s = df_s[['Номер',
             'email', 
             'Просроченное тело', 
             'Просроченные проценты', 
             'К погашению всего', 
             'Кол-во дней просрочки'
]]
df_s = df_rename_cols(df_s, {
'Номер'                 : 'app_id',
'email'                 : 'email',
'Просроченное тело'     : 'ovd_b',
'Просроченные проценты' : 'ovd_i',
'К погашению всего'     : 'to_pay',
'Кол-во дней просрочки' : 'ovd_d',
})
df_conv(df_s, {
 'app_id' : 'int',
 'email'  : 'str',
 'ovd_b'  : 'float',
 'ovd_i'  : 'float',
 'to_pay' : 'float',
 'ovd_d'  : 'int',
})
print(' - read slice')

print(' + read emails')
df_e = pd.read_csv('s_ovd.csv',
                   dtype      = str, 
                   sep        = '\t',
                   quotechar  = '"', 
                   encoding   = 'utf-8',
)
print(' - read emails')

df_s = df_s.set_index('email')
df_e = df_e.set_index('email')
df = df_join(l = df_e, r = df_s, how = 'inner')

# масив пар, индекс(строка, маска по индексу)
# создается из s_ovd.csv (тип рассылки, имейл). 
# s_ovd.csv - вручную из рассылки Вадима
vtyp = list(set(df_e.typ.to_list()))
vtup = [(t, df.typ == t) for t in vtyp] 

res_df = pd_df(index   = vtyp, 
               columns = ['ovd_b_sum','ovd_i_sum','total'])

for tup in vtup:
 typ = tup[0]
 msk = tup[1]
 idf = df[msk]
 idf = idf[~idf.duplicated()]
 res_df.loc[typ, 'ovd_b_sum'] = idf.ovd_b.sum()
 res_df.loc[typ, 'ovd_i_sum'] = idf.ovd_i.sum()
 res_df.loc[typ, 'total']     = res_df.loc[typ, 'ovd_b_sum'] + res_df.loc[typ, 'ovd_i_sum']

res_df = df_rename_cols(res_df, {
 'ovd_b_sum' : 'Просроченное тело',
 'ovd_i_sum' : 'Просроченные проценты',
 'total'     : 'Итого',
})

fn = save_e('b_', {'таблица' : res_df}, need_index = true, need_date = true)

send_mail('analytic4@creditup.com.ua',
          [
           'Вадим <postmaster@creditup.com.ua>'
          ],
          'выборка по email',
          '',
          [fn]
         )