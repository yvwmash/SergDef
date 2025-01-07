import psycopg2

from   collections import namedtuple
from   time        import time
import re

from h_pd        import *
from fop         import *
from h_types     import *

control_chars   = ''.join(map(chr, list(range(0,32)) + list(range(127,160))))
control_char_re = re.compile(r'[%s]' % re.escape(control_chars))

# ###
def pq_connect(nm):
 if nm == 'wf':
  try:
   conn = psycopg2.connect("dbname=wf user=yvmash host=/var/run/postgresql/ port=5433")
  except:
   pass
   print(' * failed to connect to postgres db %s' % nm)
   return (-1, 0)
 else:
  print('no such parameter: "'+ nm + '"')
  return (-1, 0)
 print('connected to postgres db: %s' % nm)
 return (0, conn)

# ###
def pq_close(c):
 print('closed postgres connection')
 c.close()

# ###
def pq_fetch_v(c, q, args = none):
 print('pq: start query: fetch single value')
 st = time()
 cs = c.cursor()
 cs.execute(q,args)
 res = cs.fetchone()
 nrows   = cs.rowcount
 if nrows == 0:
  return (0, 0)
 t0 = time() - st
 print('pq: done query in : %f' % t0)
 print('pq: # rows fetched: ', nrows)
 return (nrows, res[0])

# ###
def pq_fetch_r(c, q, args = none):
 print('pq: start query: fetch row')
 st = time()
 cs = c.cursor()
 cs.execute(q,args)
 tup     = cs.fetchone()
 nrows   = cs.rowcount
 if nrows == 0:
  return (0, 0)
 columns = list(map(lambda x:x.name, cs.description))
 l  = [str(v) if v != none else '' for v in tup]
 df = pd_df([l], columns = columns, dtype = str)
 for c in df.columns:
  df[c] = df[c].str.strip()
  df[c] = df[c].str.replace(control_char_re, '')
 cs.close()
 t0 = time() - st
 print('pq: done query in : %f' % t0)
 print('pq: # rows fetched: ', nrows)
 return (nrows, df)

# ###
def pq_fetch(c, q, args = none):
 print('pq: start query: fetch')
 st = time()
 cs = c.cursor()
 cs.execute(q,args)
 vtup = cs.fetchall()
 nrows   = cs.rowcount
 if nrows == 0:
  return (0, 0)
 columns = list(map(lambda x:x.name, cs.description))
 vlst = [[str(v) if v != none else '' for v in t] for t in vtup]
 df = pd.DataFrame(vlst, columns = columns, dtype = str)
 for c in df.columns:
  df[c] = df[c].str.strip()
  df[c] = df[c].str.replace(control_char_re, '')
 cs.close()
 t0 = time() - st
 print('pq: done query in : %f' % t0)
 print('pq: # rows fetched: ', nrows)
 return (nrows, df)

# ###
def pq_desc_tab(c, tab_schema, tab_nm, tab_column_names = none):
 print('pq: describe query')
 if tab_column_names:
  c_nms = ', '.join("'{0}'".format(cnm) for cnm in tab_column_names)  
 else:
  c_nms = none
 c_nms = f''' and c.COLUMN_NAME in ({c_nms})''' if c_nms else ''
 q = f'''select c.COLUMN_NAME                  as column_name, 
                c.DATA_TYPE                    as data_type, 
                c.IS_NULLABLE                  as is_nullable, 
                c.COLUMN_DEFAULT               as column_default, 
                c.CHARACTER_MAXIMUM_LENGTH     as character_maximum_length, 
                c.NUMERIC_PRECISION            as numeric_precision, 
                c.NUMERIC_SCALE                as numeric_scale
         from INFORMATION_SCHEMA.COLUMNS as c
         where c.table_name   = '{tab_nm}'
           and c.table_schema = '{tab_schema}'
      ''' + c_nms
 nrows, df  = pq_fetch(c, q)
 if nrows == 0:
  return (0, 0)
 if tab_column_names:
  lc = list(df.column_name)
  for cnm in tab_column_names:
   if cnm not in lc:
    print(f' * q: describe: no "{cnm}" found in "{tab_nm}" columns')
    return (-1, 0)
 res = pd_df(index = none, columns = df.columns)
 if tab_column_names:
  for cnm in tab_column_names:
   c = df[df.column_name == cnm].copy()
   res = df_append(res, c)
 else:
  res = df
 return (nrows, res)

def pq_exec(conn, q, vargs = none):
 cs = conn.cursor()
 cs.execute(q, vargs)
 cs.close()

exit(0)