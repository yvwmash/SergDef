from collections import namedtuple

from h_types     import *
from h_mq        import *
from h_pq        import *
from h_pd        import *

# ###
q_conn      = namedtuple('q_conn', 'conn typ')

# ###
def q_connect(nm):
 vmq = ['db_0', 'db_1']
 vpq = ['db_pq_0', 'db_pq_1']
 typ  = none
 conn = none
 if nm in vmq:
  status, conn = mq_connect(nm)
  typ          = 'mq'
 elif nm in vpq:
  status, conn = pq_connect(nm)
  typ          = 'pq'
 else:
  print('no such parameter: "'+ nm + '"')
  return (-1, q_conn(conn, typ))
 if status < 0:
  return (-1, 0)
 return (0, q_conn(conn,typ))

# ###
def q_exec(c, q, vargs = none):
 if c.typ == 'pq':
  pq_exec(c.conn,q,vargs)
 elif c.typ == 'mq':
  mq_exec(c.conn, q, vargs)
 else:
  print('wrong type passed')
  exit()

# ###
def q_commit(c):
 c.conn.commit()

# ###
def q_fetch_v(c, q, args = none):
 if c.typ == 'mq':
  return mq_fetch_v(c.conn, q, args)
 elif c.typ == 'pq':
  return pq_fetch_v(c.conn, q, args)
 else:
  print('wrong parameter passed')
  exit()

# ###
def q_fetch_r(c, q, args = none):
 if c.typ == 'mq':
  return mq_fetch_r(c.conn, q, args)
 elif c.typ == 'pq':
  return pq_fetch_r(c.conn, q, args)
 else:
  print('wrong parameter passed')
  exit()

# ###
def q_fetch(c, q, args = none):
 if c.typ == 'mq':
  return mq_fetch(c.conn, q, args)
 elif c.typ == 'pq':
  return pq_fetch(c.conn, q, args)
 else:
  print('wrong parameter passed')
  exit()

# ###
def q_desc_tab(c, tab_schema, tab_nm, tab_column_names = none):
 if c.typ == 'mq':
  nrows, df = mq_desc_tab(c.conn, tab_schema, tab_nm, tab_column_names)
  return df
 elif c.typ == 'pq':
  nrows, df = pq_desc_tab(c.conn, tab_schema, tab_nm, tab_column_names)
  return df
 else:
  print('wrong parameter passed')
  exit()

# ###
def pq_defs(pq_typ):
 if typ in ['date','varchar','text']:
  default = '\'' + default + '\'' if default else none
 elif typ == 'timestamp':
  default = '\'-infinity\''
 if typ == 'numeric':
  suff     = f'({nump},{nums})'
  pq_typed = pq_typed + suff
  typ      = typ + suff
 elif typ == 'varchar':
  suff     = f'({clen})'
  pq_typed = pq_typed + suff
  typ      = typ + suff
 return (pq_def, mq_def)

# ###
def desc_mq2pq(mq_desc):
 mq2pq = {
  'int'         : 'int',
  'tinyint'     : 'smallint',
  'decimal'     : 'numeric',
  'timestamp'   : 'timestamp',
  'datetime'    : 'timestamp',
  'date'        : 'date',
  'varchar'     : 'varchar',
  'text'        : 'text',
  'mediumtext'  : 'text',
 }
 df = pd_df(index = none, columns = ['c_nm',
                                     'db_typ',
                                     'is_nullable',
                                     'default',
                                     'c_len',
                                     'num_precision',
                                     'num_scale',
                                     'pq_typed',
                                     'is_key',
           ])
 for i, row in mq_desc.iterrows():
  nm       = row.column_name
  typ      = mq2pq[row.data_type]
  null_ok  = 1 if row.is_nullable == 'YES' else 0
  default  = row.column_default
  clen     = row.character_maximum_length
  nump     = row.numeric_precision
  nums     = row.numeric_scale
  pq_typed = nm + '::' + typ
  key      = row.column_key
  if typ in ['date','varchar','text']:
   default = '\'' + default + '\'' if default else none
  elif typ == 'timestamp':
   default = '\'-infinity\''
  if typ == 'numeric':
   suff     = f'({nump},{nums})'
   pq_typed = pq_typed + suff
   typ      = typ + suff
  elif typ == 'varchar':
   suff     = f'({clen})'
   pq_typed = pq_typed + suff
   typ      = typ + suff
  df = df_append(df, [nm,typ,null_ok,default,clen,nump,nums,pq_typed,key])
 return df

# ###
def q_map_desc(src_db, dst_db, desc):
 if src_db == 'mq' and dst_db == 'pq':
  return desc_mq2pq(desc)
 else:
  print(f'no support for q_map_desc({src_db},{dst_db})')
  exit()

# ###
def q_close(c):
 if c.typ == 'mq':
  mq_close(c.conn)
 elif c.typ == 'pq':
  pq_close(c.conn)
 else:
  print('wrong parameter passed')
  exit()

exit(0)