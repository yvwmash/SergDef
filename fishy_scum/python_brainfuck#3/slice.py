# -*- coding: utf-8 -*-

from inc import *
import inspect

def perror_exit(e_code = -1):
 print(' * line: ',inspect.currentframe().f_back.f_lineno)
 exit(e_code)

if argc < 2:
 print('usage: python slice.py <срез>')
 sys.exit(0)

fn  = argv[1]

# , skiprows = 38, header = None, index_col=0
df = pd.read_csv(fn,                    
                 dtype      = str, 
                 skiprows   = 5,
                 skipfooter = 1,
                 sep        = '\t',
                 quotechar  = '"', 
                 encoding   = 'utf-8',
                 engine     = 'python')

df.columns = [re.sub(r'\n','',x).strip() for x in df.columns.values]
df = df.loc[:, ['Задолженность по телу','Кол-во дней просрочки']].iloc[:-1]
df.loc[:, 'Кол-во дней просрочки'] = pd.to_numeric(df.loc[:, 'Кол-во дней просрочки'].astype(str), errors = 'coerce')
df.loc[:, 'Задолженность по телу'] = pd.to_numeric(df['Задолженность по телу'].astype(str), errors = 'coerce')
novd   = 0
sovd_b = 0
nstd   = 0
sstd_b = 0

#print(locale.localeconv()) #locale information
locale.setlocale(locale.LC_NUMERIC, 'uk_UA.utf8')

to_str = locale.str

mask_ovd = df.loc[:, 'Кол-во дней просрочки'] > 0
mask_std = df.loc[:, 'Кол-во дней просрочки'].isna() | df.loc[:, 'Задолженность по телу'].isna()
print('#ovd    = ', df.loc[mask_ovd].shape[0])
print('sum ovd = ', to_str(df.loc[mask_ovd, 'Задолженность по телу'].sum()))
print('#std    = ', df.loc[mask_std].shape[0])
print('sum std = ', to_str(df.loc[mask_std, 'Задолженность по телу'].sum()))