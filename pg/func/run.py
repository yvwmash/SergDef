import subprocess

_imp_path = '/mnt/db/import/'
fn        = '1.xlsx'

res = subprocess.run(["xlsx2csv", f"{_imp_path}{fn}"], stdout = subprocess.PIPE)

if res.returncode == 0:
 outp = str(res.stdout)
 outp = outp.replace(r'\n', '')
 print(outp)