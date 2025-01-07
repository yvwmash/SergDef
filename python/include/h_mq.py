from mysql.connector import connect
from mysql.connector import FieldType as __mysql_ctyp
from mysql.connector import FieldFlag as _mysql_cflags
from   collections import namedtuple
from   time        import time
import re

from h_pd        import *
from fop         import *
from h_types     import *

# structs
#

# ###
control_chars   = ''.join(map(chr, list(range(0,32)) + list(range(127,160))))
control_char_re = re.compile(r'[%s]' % re.escape(control_chars))

# ###
def mq_connect(nm):
 d_fro = {
  "us"     : "maxim",
  "host"   : "localhost",
  "port"   : 3307,
  "passw"  : "9fShTw3sHTtsTZQ6",
  "sch_nm" : "pro_creditup_cab"
 }
 d_dec = {
  "us"     : "analytic",
  "host"   : "176.9.43.166",
  "port"   : 3306,
  "passw"  : "Ld78ew29JA11",
  "sch_nm" : "creditup_dmaker"
 }
 d_ast = {
  "us"     : "analytic2",
  "host"   : "pbx.creditup.com.ua",
  "port"   : 3306,
  "passw"  : "ZX13gt87",
  "sch_nm" : "asteriskcdr"  
 }

 if   nm == 'decision':
  cc = d_dec
 elif nm == 'front':
  cc = d_fro
 elif nm == 'asterisk':
  cc = d_ast
 else:
  print('no such parameter: "'+ nm + '"')
  return (-1, 0)
 try:
  cq = connect(host      = cc['host'],
               user      = cc['us'], 
               password  = cc['passw'], 
               port      = cc['port'], 
               database  = cc['sch_nm'],
               raw       = true,
               charset   = 'utf8'
  )
 except:
  pass
  print(f' * failed to connect to mysql db {nm}')
  return (-1, 0)
 print(f'connected to mysql db: {nm}')
 return (0, cq)

# ###
def mq_close(c):
 c.close()
 print('closed mysql connection')

# ###
def mq_exec(c, q, vargs):
 cs = c.cursor()
 cs.execute(q,vargs)
 cs.close()

def mq_fetch_v(c, q, args = none):
 print('mq: start query: fetch single value')
 st = time()
 cs = c.cursor()
 cs.execute(q,args)
 columns = list(map(lambda x:x[0], cs.description))
 row     = cs.fetchone()
 nrows   = cs.rowcount
 if nrows == 0:
  return (0, 0)
 l = [str(v.decode()) if v != none else '' for v in row]
 cs.close()
 t0 = time() - st
 print('mq: done query in : %f' % t0)
 print('mq: # rows fetched: ', nrows)
 return (nrows, l[0])


def mq_fetch_r(c, q, args = none):
 print('mq: start query: fetch row')
 st = time()
 cs = c.cursor()
 cs.execute(q,args)
 columns = list(map(lambda x:x[0], cs.description))
 tup     = cs.fetchone()
 nrows   = cs.rowcount
 if nrows == 0:
  return (0, 0)
 l  = [str(v.decode()) if v != none else '' for v in tup]
 df = pd_df([l], columns = columns, dtype = str)
 for c in df.columns:
  df[c] = df[c].str.strip()
  df[c] = df[c].str.replace(control_char_re, '')
 cs.close()
 t0 = time() - st
 print('mq: done query in : %f' % t0)
 print('mq: # rows fetched: ', nrows)
 return (nrows, df)

def mq_fetch(c, q, args = none):
 print('mq: start query: fetch')
 st = time()
 cs = c.cursor()
 cs.execute(q,args)
 columns = list(map(lambda x:x[0], cs.description))
 vtup = cs.fetchall()
 nrows   = cs.rowcount
 if nrows == 0:
  return (0, 0)
 vlst = [[str(v.decode()) if v != none else '' for v in t] for t in vtup]
 df = pd.DataFrame(vlst, columns = columns, dtype = str)
 for c in df.columns:
  df[c] = df[c].str.strip()
  df[c] = df[c].str.replace(control_char_re, '')
 cs.close()
 t0 = time() - st
 print('mq: done query in : %f' % t0)
 print('mq: # rows fetched: ', nrows)
 return (nrows, df)

# ###
def mq_desc_tab(c, tab_schema, tab_nm, tab_column_names = none):
 print('mq: describe query')
 if tab_column_names:
  c_nms = ', '.join("'{0}'".format(cnm) for cnm in tab_column_names)
 else:
  c_nms = none
 c_nms = f''' and COLUMN_NAME in ({c_nms})''' if c_nms else ''
 q = f'''select COLUMN_NAME                  as column_name, 
                DATA_TYPE                    as data_type, 
                IS_NULLABLE                  as is_nullable, 
                COLUMN_DEFAULT               as column_default, 
                CHARACTER_MAXIMUM_LENGTH     as character_maximum_length, 
                NUMERIC_PRECISION            as numeric_precision, 
                NUMERIC_SCALE                as numeric_scale,
                COLUMN_KEY                   as column_key,
                EXTRA                        as extra
         from INFORMATION_SCHEMA.COLUMNS
         where table_name   = '{tab_nm}'
           and table_schema = '{tab_schema}'
      ''' + c_nms
 nrows, df  = mq_fetch(c, q)
 if tab_column_names:
  lc = list(df.column_name)
  for cnm in tab_column_names:
   if cnm not in lc:
    print(f' * q: describe: no "{cnm}" found in "{tab_nm}" columns')
    return (-1, 0)
 if nrows == 0:
  return (0, 0)
 res = pd_df(index = none, columns = df.columns)
 if tab_column_names:
  for cnm in tab_column_names:
   c = df[df.column_name == cnm].copy()
   res = df_append(res, c)
 else:
  res = df
 return (nrows, res)