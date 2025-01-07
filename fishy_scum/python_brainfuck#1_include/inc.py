from datetime import date
from datetime import datetime
from time import time

import re
import collections
import calendar
import requests
import difflib

# ###
from h_types import *
from h_pd    import *
from h_ssh   import *
from h_email import *
from h_excel import *
from h_q     import *

# ###
def last_day(year, month):
 return calendar.monthrange(year, month)[1]

# ###
def ssep_list(l, sep = ', '):
 return ', '.join("{0}".format(v) for v in l)

# ###
def ssep_listq(l):
 return ', '.join("'{0}'".format(v) for v in l)