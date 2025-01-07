import json
import sys
import os.path

dirname = os.path.dirname

script_rpath = sys.argv[0]
data_rpath   = dirname(script_rpath) + '/' + 'data0.json'

from h_types     import *

# FUNCTION  : read_f
#             read file as string
#
# fn        - file path

# FUNCTION  : read_json_f
#             read JSON file as string
#
# fn - file path

# ###
def read_f(fn):
 f = open(fn, encoding = 'utf8')
 s = f.read()
 f.close()
 return s

# ###
def read_json_f(fn):
 f = open(fn, encoding = 'utf8')
 js = json.load(f)
 f.close()
 return js

f = read_f(data_rpath)
print(f)
f = read_json_f(data_rpath)
print(f)

exit(0)