import pandas as pd
import re

from h_types     import *

# ###
pd.options.display.max_rows = 1000
pd.set_option('display.float_format', lambda x: '%.3f' % x)

pd_df = pd.DataFrame
pd_se = pd.Series

# ###
control_chars   = ''.join(map(chr, list(range(0,32)) + list(range(127,160))))
control_char_re = re.compile(r'[%s]' % re.escape(control_chars))

# ###
def df_minus(src_df, arg_df):
 return src_df[~src_df.index.isin(arg_df.index)].copy()

# ### 
def df_len(df):
 return df.shape[0]

# ###
def df_append(l,r):
 if isinstance(r, list):
  r = pd_se(data = r, index = l.columns)
 elif isinstance(r, pd.DataFrame):
  r = r.iloc[0]
 elif isinstance(r, pd.Series):
  r = pd_se(data = r.values, index = l.columns)
 else:
  print(' * df_append: not supported type')
  exit()
 return l.append(r, ignore_index = true)

# ###
def df2ff(df):
 for c in df.columns:
  if df[c].dtype == np.float64:
   df[c] = c_conv(df[c], 'str')
   df[c] = df[c].str.replace('.', ',')
   df[c] = c_conv(df[c], 'float')

# ###
def df_to_tuples(df, need_names = none):
 return list(df.itertuples(index = false, name = need_names))

# ###
def df_join(l,r,how):
 return pd.merge(l, r, how = how, left_index = true, right_index = true, sort = false)

# ###
def df_merge(l,r,how,l_on = none, r_on = none, l_i = false, r_i = false):
 return pd.merge(l, r, how = how, left_on = l_on, right_on = r_on, left_index = l_i, right_index = r_i, sort = false)

# ###
def df_c2datetime(c):
 return pd.to_datetime(c, errors = 'coerce')

# ###
def c_conv(c, typ):
 if typ == 'float':
  c = c.fillna(0)
  c = c.astype(str)
  c = c.str.replace(r'\s+', '')
  c = c.str.replace(r'^$', '0')
  c = c.str.replace(r',', '.')
  return c.astype(float)
 elif typ == 'int':
  c = c.fillna(0)
  c = c.astype(str)
  c = c.str.replace(r'\s+', '')
  c = c.str.replace(r'^$', '0')
  c = c.astype(float)
  return c.astype(int)
 elif typ == 'str':
  c = c.fillna('')
  c = c.astype(str)
  c = c.str.strip()
  c = c.str.replace(control_char_re, '')
  return c
 elif typ == 'date':
  c = df_c2datetime(c)
  return c.dt.date
 elif typ == 'datetime':
  return df_c2datetime(c)

def df_conv(df, typ_map):
 for c_nm, c_typ in typ_map.items():
  if c_nm not in df.columns:
   continue
  df[c_nm] = c_conv(df[c_nm], c_typ)

def df_rename_cols(df, c_dict):
 df = df.rename(columns = c_dict)
 return df

exit(0)