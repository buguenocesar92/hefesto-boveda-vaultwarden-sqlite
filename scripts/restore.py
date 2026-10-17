#!/usr/bin/env python3
import hashlib,json,os,subprocess,sys
from pathlib import Path
from archive_check import check_archive
root=Path(__file__).resolve().parents[1];os.chdir(root)
if len(sys.argv)!=2:raise SystemExit('Uso: python3 scripts/restore.py /ruta/respaldo')
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text())
required={'data.tar.gz','.env','compose.yaml','compose.smtp.yaml'}
if m.get('status')!='completed' or set(m.get('sha256',{}))!=required:raise SystemExit('Manifest incompleto')
for n in required:
    with (p/n).open('rb') as f:
        if hashlib.file_digest(f,'sha256').hexdigest()!=m['sha256'][n]:raise SystemExit('Hash incorrecto: '+n)
check_archive(p/'data.tar.gz')
def dc(*a,**kw):return subprocess.run(['docker','compose',*a],check=True,**kw)
if not (root/'.env').is_file():raise SystemExit('Preparar .env destino según docs/operacion.md')
if dc('ps','--status','running','-q','app',capture_output=True,text=True).stdout.strip():raise SystemExit('app debe estar detenida')
found=dc('run','--rm','--no-deps','-T','--user','0','--entrypoint','find','app','/data','-mindepth','1','-maxdepth','1',capture_output=True,text=True).stdout.strip()
if found:raise SystemExit('Volumen no vacío; no se sobrescribe')
with (p/'data.tar.gz').open('rb') as f:
    dc('run','--rm','--no-deps','-T','--user','0','--entrypoint','tar','app','-xzf','-','-C','/data',stdin=f)
print('Restaurado. Revisar configuración heredada y arrancar app; realizar aceptación. Ante fallo parcial usar un volumen nuevo.')
