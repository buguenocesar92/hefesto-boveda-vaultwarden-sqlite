#!/usr/bin/env python3
import os,re,sys
from pathlib import Path
if len(sys.argv)!=4 or not re.fullmatch(r'[a-z][a-z0-9-]{2,39}',sys.argv[1]) or not re.fullmatch(r'(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}',sys.argv[2]) or not re.fullmatch(r'[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',sys.argv[3]):
    raise SystemExit('Uso: python3 scripts/configure.py cliente-demo boveda.tudominio.cl propietario@tudominio.cl')
root=Path(__file__).resolve().parents[1];prefix='hefesto-boveda-'+sys.argv[1]
values={'COMPOSE_PROJECT_NAME':prefix,'VOLUME_PREFIX':prefix,'VAULT_HOST':sys.argv[2],'OWNER_EMAIL':sys.argv[3]}
try:fd=os.open(root/'.env',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
except FileExistsError:raise SystemExit('.env ya existe; no se modificó.')
with os.fdopen(fd,'w') as f:
    for k,v in values.items():f.write(k+"='"+v+"'\n")
print('.env creado con permisos 0600. La contraseña maestra la establece el usuario en la bóveda; no se genera aquí.')
