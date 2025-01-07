from inc import *
import inspect

# портфель по групам просрочки
# файл на входе - результат среза для отделов сбора(cslice.py <срез для договоров> <срез для контактов>)
# возможно файл среза нужно отредактировать вручную

def perror_exit(e_code = -1):
 print(' * line: ',inspect.currentframe().f_back.f_lineno)
 exit(e_code)

if argc == 0:
 print('usage: python3 s_by_groups.py')
 sys.exit(0)

print('read file')
df = pd.read_excel('s_by_groups.xlsx', dtype = str, encoding = 'utf-8')

print('types')
df_conv(df,{
           'Номер'                   : 'int',
           'ИНН'                     : 'str',
           'ФИО'                     : 'str',
           'nloans - (mysql)'        : 'int',
           'dpr'                     : 'float',
           'Выдано по договору'      : 'int',
           'Кол-во дней просрочки'   : 'int',
           'RR'                      : 'float',
           'Просроченное тело'       : 'float',
           'Просроченные проценты'   : 'float',
           'К погашению всего'       : 'float',
           'Сотрудник'               : 'str',
           'Группа просрочки'        : 'str',
           'new/repeat - (1C)'       : 'str',
           'моб. тел'                : 'str',
           'email'                   : 'str',
           'заморожен'               : 'int',
           'Дата Рождения'           : 'date',
           'Возраст'                 : 'int',
           'Пол'                     : 'str',
           'Адрес прописки'          : 'str',
           'Город'                   : 'str',
           'Работа'                  : 'str',
           'Последний контакт'       : 'str',
})
df = df[['Номер',
         'nloans - (mysql)',
         'new/repeat - (1C)',
         'dpr',
         'Выдано по договору',
         'Кол-во дней просрочки',
         'Просроченное тело',
         'Просроченные проценты',
         'К погашению всего',
         'заморожен',
]]
df['ovd_group']             = np.nan
df['loan_to_pay']           = np.nan
df['loan_issued']           = np.nan
df['new/repeat - (mysql)']  = np.nan

print('masks & groups')
mask_o_0_90    = (df['Кол-во дней просрочки'] <= 90)
mask_o_91_180  = (df['Кол-во дней просрочки'] >= 91)  & (df['Кол-во дней просрочки'] <= 180)
mask_o_181_360 = (df['Кол-во дней просрочки'] >= 181) & (df['Кол-во дней просрочки'] <= 360)
mask_o_360_p   = (df['Кол-во дней просрочки'] >  360)

mask_ls_1000      = (df['К погашению всего'] <= 1000)
mask_ls_1000_1500 = (df['К погашению всего'] >= 1000) & (df['К погашению всего'] <= 1500)
mask_ls_1500_3000 = (df['К погашению всего'] >= 1500) & (df['К погашению всего'] <= 3000)
mask_ls_3000_6000 = (df['К погашению всего'] >= 3000) & (df['К погашению всего'] <= 6000)
mask_ls_6000_p    = (df['К погашению всего'] > 6000)

mask_li_1000      = (df['Выдано по договору'] <= 1000)
mask_li_1000_1500 = (df['Выдано по договору'] >= 1000) & (df['Выдано по договору'] <= 1500)
mask_li_1500_3000 = (df['Выдано по договору'] >= 1500) & (df['Выдано по договору'] <= 3000)
mask_li_3000_6000 = (df['Выдано по договору'] >= 3000) & (df['Выдано по договору'] <= 6000)
mask_li_6000_p    = (df['Выдано по договору'] > 6000)

mask_new = (df['nloans - (mysql)'] <= 1)
mask_rep = (df['nloans - (mysql)']  > 1)

df.loc[mask_o_0_90, 'ovd_group']    = '0-90'
df.loc[mask_o_91_180, 'ovd_group']  = '91-180'
df.loc[mask_o_181_360, 'ovd_group'] = '181-360'
df.loc[mask_o_360_p, 'ovd_group']   = '360+'

df.loc[mask_ls_1000, 'loan_to_pay']      = '0-1000'
df.loc[mask_ls_1000_1500, 'loan_to_pay'] = '1000-1500'
df.loc[mask_ls_1500_3000, 'loan_to_pay'] = '1500-3000'
df.loc[mask_ls_3000_6000, 'loan_to_pay'] = '3000-6000'
df.loc[mask_ls_6000_p, 'loan_to_pay']    = '6000+'

df.loc[mask_li_1000, 'loan_issued']      = '0-1000'
df.loc[mask_li_1000_1500, 'loan_issued'] = '1000-1500'
df.loc[mask_li_1500_3000, 'loan_issued'] = '1500-3000'
df.loc[mask_li_3000_6000, 'loan_issued'] = '3000-6000'
df.loc[mask_li_6000_p, 'loan_issued']    = '6000+'

df.loc[mask_new, 'new/repeat - (mysql)'] = 'новый'
df.loc[mask_rep, 'new/repeat - (mysql)'] = 'повторный'

print('save')
df.to_excel('o.xlsx', index = false)