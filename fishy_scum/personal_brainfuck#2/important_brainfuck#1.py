# -*- coding: utf-8 -*-

from inc import *
import inspect

print(' + read slice')
df_s = pd.read_csv('/mnt/hdd/db_io/1C/201911/s_21.csv',
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
df_conv(df_s, {
'Номер'                    : 'int',
'ИНН'                      : 'str',
'Выдано по договору'       : 'float',
'Кол-во дней просрочки'    : 'int',
'Просроченное тело'        : 'float',
'Просроченные проценты'    : 'float',
'Дата факт закрытия'       : 'date'
})
df_s = df_s[['email',
             'Номер',
             'ИНН',
             'Просроченное тело',
             'Просроченные проценты',
             'Дата факт закрытия',
]]
df_s = df_s.rename(
 columns = {
 'Номер'                    : 'app_id',
 'Кол-во дней просрочки'    : 'dovd',
 'Просроченное тело'        : 'ovd_b',
 'Просроченные проценты'    : 'ovd_i',
 'ИНН'                      : 'inn',
 'Дата факт закрытия'       : 'dt_closed'
 }
)
print(' - read slice')

print(' + read emails')
df_e = pd.read_csv('s_ovd.csv',
                   dtype      = str, 
                   sep        = '\t',
                   quotechar  = '"', 
                   encoding   = 'utf-8',
)
print(' - read emails')

df_s = df_s.set_index('app_id')
df_e = df_e.set_index('app_id')
df = df_join(l = df_e, r = df_s, how = 'inner')
#~ df = df[~df.inn.duplicated()]

#~ idf = df.groupby(['inn']).sum()
#~ idf['total'] = np.nan
#~ idf.total = idf.ovd_b + idf.ovd_i

print(df)
exit()

fn = save_e('brief_',{'портфель' : res_df}, need_date = 1, need_index = 1)

send_mail('analytic4@creditup.com.ua',
          ['Лазепка Валентин Игоревич <lazepkav@creditup.com.ua>',
           'Сергей Романович <ssr@creditup.com.ua>', 
           'Ирина <operator05@creditup.com.ua>',
           'Сергей <analytic3@creditup.com.ua>'
          ],
           'портфель, 1-30, 31-60, 61-90',
          '',
          [fn]
         )