#!/usr/bin/env python3
"""Validate trusted local backup layout and SQLite integrity without extracting arbitrary paths."""
import shutil,sqlite3,tarfile,tempfile
from pathlib import PurePosixPath,Path
def check_archive(path):
    with tarfile.open(path,'r:gz') as tf:
        names={};dbfiles={}
        for m in tf:
            p=PurePosixPath(m.name)
            if p.is_absolute() or '..' in p.parts or not(m.isfile() or m.isdir()):raise ValueError('Ruta/tipo de archivo no admitido')
            n=str(p)
            if n in names:raise ValueError('Ruta duplicada en tar')
            names[n]=True
            if n in {'db.sqlite3','db.sqlite3-wal','db.sqlite3-shm'}:
                if not m.isfile():raise ValueError('Base no es archivo regular')
                dbfiles[n]=m
        if 'db.sqlite3' not in dbfiles:raise ValueError('No hay base SQLite en el respaldo')
        # Temporary directory is private; copy only fixed database filenames.
        with tempfile.TemporaryDirectory(prefix='hefesto-vault-check-') as t:
            for n,m in dbfiles.items():
                with tf.extractfile(m) as src,(Path(t)/n).open('wb') as dest:shutil.copyfileobj(src,dest)
            with sqlite3.connect(str(Path(t)/'db.sqlite3')) as db:
                if db.execute('PRAGMA quick_check').fetchall()!=[('ok',)]:raise ValueError('SQLite quick_check falló')
                if db.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='users'").fetchone()[0]!=1:raise ValueError('No se reconoce la tabla users de Vaultwarden')
