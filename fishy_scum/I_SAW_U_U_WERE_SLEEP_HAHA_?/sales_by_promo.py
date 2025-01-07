# -*- coding: utf-8 -*-

# Роману
#

from inc import *
import inspect

def perror_exit(e_code = -1):
 print(' * line: ',inspect.currentframe().f_back.f_lineno)
 exit(e_code)

if argc < 1 or argc > 2:
 print('usage: python sales_by_promo.py')
 exit(0)

q = f'''
SELECT CONVERT(TRIM(JSON_UNQUOTE(JSON_EXTRACT(extended, '$.promo_code'))) USING utf8) as promo_code
FROM finplugs_creditup_applications ap
WHERE
	date(ap.applied_at) >= dt_min and date(ap.applied_at) <= dt_max
	and status_id in (4,5,6)
 and ap.product_id IN (12, 23, 28, 29, 33, 35, 36, 42, 44, 52, 76, 77, 78, 79)
;
'''

status, con = q_connect('front')
if status < 0:
 perror_exit()

nrows, df = q_fetch(con, rq)
q_close(cs, cq)

# process ###

# save ###########################################################################################################################################

#~ vdf = {'out': df}
#~ save_e('',vdf, 1, 0)
