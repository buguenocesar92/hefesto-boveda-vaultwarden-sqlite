#!/usr/bin/env python3
import datetime,hashlib,json,os,subprocess
from pathlib import Path
from archive_check import check_archive
root=Path(__file__).resolve().parents[1];os.chdir(root);os.umask(0o077)
def dc(*a,**kw):return subprocess.run(['docker','compose',*a],check=True,**kw)
if not (root/'.env').is_file():raise SystemExit('Falta .env')
if not dc('ps','--status','running','-q','app',capture_output=True,text=True).stdout.strip():raise SystemExit('app no está activa en este contexto Compose')
p=root/'backups'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');p.mkdir(parents=True)
try:
    dc('stop','app')
    # All of /data, including db + matching WAL, attachments and signing keys.
    with (p/'data.tar.gz').open('wb') as f:
        dc('run','--rm','--no-deps','-T','--user','0','--entrypoint','tar','app','-czf','-','-C','/data','.',stdout=f)
    for n in ['.env','compose.yaml','compose.smtp.yaml']:(p/n).write_bytes((root/n).read_bytes())
finally:dc('start','app')
check_archive(p/'data.tar.gz')
hashes={}
for f in p.iterdir():
    with f.open('rb') as stream:hashes[f.name]=hashlib.file_digest(stream,'sha256').hexdigest()
(p/'manifest.json').write_text(json.dumps({'status':'completed','version':'1.37.4','sha256':hashes},indent=2))
print('Respaldo completo:',p,'Contiene datos y claves; cifrar y copiar fuera del VPS.')
