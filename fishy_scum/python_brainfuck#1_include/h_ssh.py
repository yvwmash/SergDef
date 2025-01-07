from fabric import Connection as fcon

from h_types     import *

# ###
def ssh_port_fwd(host, user, port, passwd, remote_port, local_port, remote_host, local_host):
 #~ cc = read_json_f('../include/creds')['serv']
 try:
  #~ c = fcon(host = cc['host'], 
              #~ user = cc['us'], 
              #~ port = cc['port'], 
              #~ connect_kwargs={"password": cc['passw'], "allow_agent" : false, "compress": false}
     #~ )
  c = fcon(host = host, 
           user = user, 
           port = port, 
           connect_kwargs={"password": passwd, "allow_agent" : false, "compress": false}
  )
 except:
  pass
  return (-1, 0)
 print('connected to ', host)
 c.forward_local(remote_port = remote_port, 
                 local_port  = local_port, 
                 local_host  = local_host, 
                 remote_host = remote_host)
 return (0, c)

