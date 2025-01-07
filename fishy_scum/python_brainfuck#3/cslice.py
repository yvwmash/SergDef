from inc import *
import inspect

# таблица для отделов сбора
# два среза из 1С и выборка из сайта в одну таблицу
# рассылка ежедневно с утра

def perror_exit(e_code = -1):
 print(' * line: ',inspect.currentframe().f_back.f_lineno)
 exit(e_code)

if argc < 3:
 print('usage: python cslice.py <срез std> <срез contacts>')
 sys.exit(0)
if argc == 3:
 fs = argv[1]
 fc = argv[2]

## query
print('query')
rq = read_f('cslice.sql')
status, mq_conn = q_connect('front')
if status < 0:
 perror_exit()
nrows, loans = q_fetch(mq_conn, rq)
q_close(mq_conn)
############################################################################

## excel
print('excel')
std = pd.read_excel(fs, dtype = str, skiprows = 5, )
con = pd.read_excel(fc, dtype = str, skiprows = 5, )
std = std.iloc[:-1]
con = con.iloc[:-1]

std.columns = std.columns.str.strip()
std.columns = std.columns.str.replace(r'\s+',' ')
con.columns = con.columns.str.strip()
con.columns = con.columns.str.replace(r'\s+',' ')

std = std[['Номер',
           'ИНН',
           'Выдано по договору',
           'Кол-во дней просрочки',
           'RR',
           'Просроченное тело',
           'Просроченные проценты',
           'Погашено по телу',
           'Погашено процентов',
           'К погашению всего',
           'Процентная ставка',
           'Сотрудник',
           'Группа просрочки',
           'Повторный / Новый',
           'моб. тел',
           'email',
           'заморожен',
           'Дата Рождения',
           'Возраст',
           'Пол',
           'Адрес прописки',
]]
con = con[['Номер',
           'ФИО',
           'Город',
           'Работа',
           'Последний контакт',
]]

std = std.fillna('0')
con = con.fillna('0')

df_conv(std, 
       {'Номер'                       : 'str',
        'ИНН'                         : 'str',
        'Выдано по договору'          : 'float',
        'Кол-во дней просрочки'       : 'int',
        'RR'                          : 'float',
        'Просроченное тело'           : 'float',
        'Просроченные проценты'       : 'float',
        'Погашено по телу'            : 'float',
        'Погашено процентов'          : 'float',
        'К погашению всего'           : 'float',
        'Сотрудник'                   : 'str',
        'Группа просрочки'            : 'str',
        'Повторный / Новый'           : 'str',
        'моб. тел'                    : 'str',
        'email'                       : 'str',
        'заморожен'                   : 'str',
        'Дата Рождения'               : 'date',
        'Возраст'                     : 'int',
        'Пол'                         : 'str',
        'Адрес прописки'              : 'str',
        'Процентная ставка'           : 'float',
})
df_conv(con, 
       {'Номер'              : 'str',
        'ФИО'                : 'str',
        'Город'              : 'str',
        'Работа'             : 'str',
        'Последний контакт'  : 'str',
})

std = std.set_index('Номер')
con = con.set_index('Номер')

df = df_join(std,con,'left')
df = df.reset_index()
############################################################################

## join query with excel
print('join q & excel')
df_conv(loans,
       {'social_number' : 'str',
        'nloans'        : 'int'
})
loans.columns = ['ИНН','nloans']
loans = loans.set_index('ИНН')
df    = df.set_index('ИНН')
df = df_join(df,loans,'left')
############################################################################

## save
print('save')
df = df.reset_index()
df = df[[  'Номер',
           'ИНН',
           'ФИО',
           'nloans',
           'Процентная ставка',
           'Выдано по договору',
           'Кол-во дней просрочки',
           'RR',
           'Просроченное тело',
           'Просроченные проценты',
           'К погашению всего',
           'Погашено по телу',
           'Сотрудник',
           'Группа просрочки',
           'Повторный / Новый',
           'моб. тел',
           'email',
           'заморожен',
           'Дата Рождения',
           'Возраст',
           'Пол',
           'Адрес прописки',
           'Город',
           'Работа',
           'Последний контакт',
]]

df = df.rename(columns = {
 'Повторный / Новый' : 'new/repeat - (1C)',
 'nloans'            : 'nloans - (mysql)',
 'Процентная ставка' : 'dpr',
})

# ####

fn = save_e('s_', {'срез' : df},
       need_date = 1, need_index = 0
      )
send_mail('analytic4@creditup.com.ua',
          ['Руслана Черняк <softcol@creditup.com.ua>', 
           'Анна <soft1@creditup.com.ua>',
           'Денис <operator50@creditup.com.ua>',
           'Александр Гордиенко <operator31@creditup.com.ua>',
           'Ирина <operator05@creditup.com.ua>',
           'Михаил <admin2@creditup.com.ua>'
          ],
          'срез отделам сбора',
          '',
          [fn]
         )