import json

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