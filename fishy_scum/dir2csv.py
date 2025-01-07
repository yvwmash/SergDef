# -*- coding: utf-8 -*-

from inc import *
import inspect

import glob

def perror_exit(e_code = -1):
 print(' * line: ',inspect.currentframe().f_back.f_lineno)
 exit(e_code)

def p2csv(gpath):
 l = [f for f in glob.glob(gpath)]
 for f in l:
  p = os.path.splitext(f)[0]
  n = os.path.basename(p)
  t = p + '.csv'
  df = pd.read_excel(f, header = none, index_col = none, dtype = object)
  df.to_csv(t, sep = '\t', header = false, index = false, decimal = ',')
  os.remove(f)
  print(t)

print(' + /mnt/hdd/db_io/loan/*.xls:')
p2csv('/mnt/hdd/db_io/loan/*.xls')
print(' - /mnt/hdd/db_io/loan/*.xls:')

print(' + /mnt/hdd/db_io/1C/*/*.xls:')
p2csv('/mnt/hdd/db_io/1C/*/*.xls')
print(' - /mnt/hdd/db_io/1C/*/*.xls:')

print(' + /mnt/hdd/db_io/collect/*/*.xls:')
p2csv('/mnt/hdd/db_io/collect/*/*.xls')
print(' - /mnt/hdd/db_io/collect/*/*.xls:')

print(' + /mnt/hdd/db_io/marketing/*/*.xls:')
p2csv('/mnt/hdd/db_io/marketing/*/*.xls')
print(' - /mnt/hdd/db_io/marketing/*/*.xls:')

