# -*- coding: utf-8 -*-

from inc import *
import inspect

import csv
import templates

#agent/calls
# agent     = 1003
#campid     = 1055
#user group = 3
# from      = 2017-01-01T00:00:00
#to         = 2019-09-23T00:00:00

# agents = 1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, va1038001 
# agents = 4,    5,    6,    7,    8,    18,   19,   20,   21,   22,   78

def perror_exit(e_code = -1):
 print(' * line: ',inspect.currentframe().f_back.f_lineno)
 exit(e_code)

# eyJhbGciOiJIUzUxMiJ9.eyJkZWxldGVTY3JpcHRzIjp0cnVlLCJtb2RpZnlVc2VycyI6dHJ1ZSwiZGVsZXRlVXNlcnMiOnRydWUsIm1vZGlmeUNhbXBhaWducyI6dHJ1ZSwibW9kaWZ5U2NyaXB0cyI6dHJ1ZSwidXNlcklkIjoiMTYiLCJkZWxldGVJbmJvdW5kR3JvdXBzIjp0cnVlLCJkZWxldGVDYW1wYWlnbnMiOnRydWUsImNsaWVudFR5cGUiOiJ1c2VyIiwidXNlckxldmVsIjo5LCJ2aWV3UmVwb3J0cyI6dHJ1ZSwiZGVsZXRlTGlzdHMiOnRydWUsIm1vZGlmeUxlYWRzIjp0cnVlLCJtb2RpZnlMaXN0cyI6dHJ1ZSwidXNlcm5hbWUiOiJkZXZlbG9wZXIiLCJtb2RpZnlJbmJvdW5kR3JvdXBzIjp0cnVlfQ.Y6Lwm3qGhKb0aH0seuF6_7hcaEMSSV81AI5ZqX46w1N_7I0L_NnbLww7MyraKtYbEdG1EFKK_B0Ij82KS7Hzcw

stoday = date.today().strftime('%d.%m.%Y')

js = read_json_f('../include/creds')['iptel']
payload = '{"username" : "' + js['us'] + '",' + '"password" : "' + js['passw'] + '"}'

header = {'Content-Type':'application/json; charset=utf-8', 'Accept':'application/json; text/html'}

r = requests.post('https://creditup.iptel.ua:8443/osdialapi/rest/login', data = payload, headers = header)
print('auth:', r.status_code, r.reason, '\n*** *** *** *** ***')

tok = json.loads(r.text)['token']

header['Authorization'] = 'Bearer ' + tok

def get_camps():
 r = requests.get('https://creditup.iptel.ua:8443/osdialapi/rest/admin/campaigns', headers = header)
 return pd.read_json(r.text)

def get_users():
 r = requests.get('https://creditup.iptel.ua:8443/osdialapi/rest/admin/users', headers = header)
 return pd.read_json(r.text)

def get_camp_by_nm(nm):
 v = get_camps()
 v = v[v.name.str.lower() == nm.lower()]
 return v if not v.empty else false

def get_cid_by_nm(nm):
  return get_camp_by_nm(nm).id
  
def get_camp_by_id(cid):
 v = get_camps()
 v = v[v.id == cid]
 return v if not v.empty else false

def get_lists():
 r = requests.get('https://creditup.iptel.ua:8443/osdialapi/rest/admin/lists', headers = header)
 return pd.read_json(r.text)

def get_list_by_nm(nm):
 v = get_lists()
 v = v[v.name.lower() == nm.lower()]
 return v if not v.empty else false

def get_list_by_id(id):
 v = get_lists()
 v = v[v.id == id]
 return v if not v.empty else false

def get_lists_by_cid(cid):
 l = get_lists()
 return l[l.campaignId.isin(cid)]

def del_list(lid):
 r = requests.delete('https://creditup.iptel.ua:8443/osdialapi/rest/admin/lists/' + str(lid), headers = header)
 return r.status_code

def creat_list(cid, lid, nm):
 data = templates.list.copy()
 tm = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
 data['changeDateTime'] = tm
 data['campaignId']     = cid
 data['id']             = lid
 data['name']           = nm
 data = json.dumps(data)
 r = requests.post('https://creditup.iptel.ua:8443/osdialapi/rest/admin/lists', headers = header, data = data)
 print('creat list: ', r.content)
 return r.status_code

def get_leads_by_lid(lid):
 r = requests.get('https://creditup.iptel.ua:8443/osdialapi/rest/admin/leads/getByListId/' + str(lid), headers = header)
 v = pd.read_json(r.text)
 return (0, v) if not v.empty else (-1, 0)

def get_lists_by_cnm(cnm):
 cid = get_cid_by_nm(cnm)
 l = get_lists()
 return l[l.campaignId.isin(cid)]

def get_leads_by_cnm(cnm):
 vlid = get_lists_by_cnm(cnm).id # series of list id
 l = {}
 for lid in vlid:
  status, vu = get_leads_by_lid(lid)
  l[lid] = vu
 return l

def put_leads_csv(lid, fn):
 if not os.path.exists(fn):
  print(' ! no such file : ', fn)
  return -1
 leads = pd.read_csv(fn, sep=';', dtype = str, encoding = 'utf-8', index_col = False)
 leads = leads.rename({'full_nm':'firstName', 'phone':'phoneNumber'}, axis = 'columns')
 tail = list(set(templates.lead.keys()) - set(leads.columns.values))
 for v in tail:
  leads[v] = ''
 tm = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
 leads.id                = -1
 leads.listId            = lid
 leads.entryDate         = tm
 leads.status            = "NA"
 leads.user              = "Y"
 leads.cost              = 0
 leads.gmtOffsetNow      = 0

 data = leads.to_json(force_ascii = False, orient = 'records').encode('utf-8')
 r = requests.post('https://creditup.iptel.ua:8443/osdialapi/rest/admin/leads/batchInsert', headers = header, data = data)
 return r.status_code

def get_stat_camp_by_lid(dt_b, dt_e, lid):
 lst = get_list_by_id(lid)
 cid = lst.campaignId.values[0]
 cnm = get_camp_by_id(cid).iloc[0].values[1]
 vagents = ['1000','1001','1002','1003','1004','1005','1006','1007','1008','1009','va1038001']
 payload = {
  'from'     : dt_b,
  'to'       : dt_e,
  'agent'    : '',
  'campaigns': str(cid),
  'userGroup': '3',
 }
 df = pd_df(index = none, columns = [
             'op',
             'ncalls',
             'time_total',
             'pause_total',
             'pause_avg',
             'wait_total',
             'wait_avg',
             'call_duration_avg',
             'dispo_time',
             'dispo_avg',
             ]
           )
 for v in vagents:
  payload['agent'] = v
  r = requests.get('https://creditup.iptel.ua:8443/osdialapi//rest/admin/reports/agent/calls/',
                   params = payload,
                   headers = header
                  )
  v = pd.read_json(r.text)
  if not v.empty:
   row = v.iloc[0]
   op = row.user['username']
   row = row[1:]
   l   = row.tolist()
   l.insert(0, op) 
   df = df_append(df, l)
 return (0, cnm, df) if not df.empty else (r.status_code, cnm, 0)

# get statistics by list_id
lid = 1746
status, cnm, df = get_stat_camp_by_lid('2019-10-25T00:00:00', '2019-10-31T00:00:00', lid)
if status == 0:
 print(f'camp name = {cnm}')
 save_e('iptel_stat_camp_' + cnm + '_10.25-10.31', {cnm : df}, need_date = false, need_index = false)
else:
 print('empty')


## find iptel by phone ########################################################
# df = pd.DataFrame(columns = templates.lead.keys(), dtype = str, data = None)

# vlid = get_lists().id
# for lid in vlid:
 # status, vlead = get_leads_by_lid(lid)
 # if status < 0:
  # continue
 # phones = vlead.phoneNumber.astype(str)
 # print(lid, 'phone exp: ', phones.iloc[0])
 # mask = phones == '380969219050'
 # if mask.any():
  # print(' ~~~~~~~~~~ found in lid : ', lid)
  # f = vlead[mask].copy()
  # f['iptel id списка']
  # df = df.append(vlead[mask])

# df.to_excel('out.xlsx', index = false)
########################################################

# l0 = get_list_by_id(1307)
# l1 = get_list_by_id(1436)
# l2 = get_list_by_id(1444)
# l3 = get_list_by_id(1450)
# l4 = get_list_by_id(1473)

# print(l0.name)
# print(l1.name)
# print(l2.name)
# print(l3.name)
# print(l4.name)


#~ cid = get_cid_by_nm('Soft1_operator48')
#~ print(cid)
#vlid  = get_lists_by_cid(cid).id
#l = {}
# for lid in vlid:
 # vu = get_leads_by_lid(lid)
 # l[lid] = vu

# print(len(l))

#vlid  = get_lists_by_cnm('test campaign').id # series of list id
#vlead = get_leads_by_cnm('08072019_91-180')
#l = vlead[1076]
#print(l.status)

# c = get_camp_by_id(1033).dialStatuses
# cc = get_camp_by_id(1033).AutoAltDialStatuses
# ccc = get_camp_by_id(1033).AutoAltDialStatuses
# print(c, cc, ccc)



#print(put_leads_csv(1381,'us.csv'))
#print(get_leads_by_id(1381))
#v = get_leads_id(1210)
#print(v.iloc[0,:])
