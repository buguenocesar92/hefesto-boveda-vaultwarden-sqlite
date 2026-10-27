#!/usr/bin/env python3
"""Respaldo de la boveda de contrasenas (Vaultwarden + SQLite).

El .env nunca se copia en claro: al respaldo solo van sus nombres (env.vars) y,
si hay receptor age, el .env cifrado (env.age). El volumen /data incluye la
base, su WAL y las claves de firma. Ver docs/CONTRATO-RESPALDO.md.
"""
import datetime
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from archive_check import check_archive
from respaldo_contrato import (artefactos_presentes, escribir_manifiesto, ejecutar,
                               exportar_env, marcar_fallido)

SOFTWARE = "hefesto-boveda"
VERSION = "1.37.4"
DATABASE = "sqlite"
RAIZ = Path(__file__).resolve().parents[1]
os.chdir(RAIZ)
os.umask(0o077)


def dc(*a, **kw):
    return subprocess.run(["docker", "compose", *a], check=True, **kw)


def main():
    if not (RAIZ / ".env").is_file():
        raise SystemExit("Falta .env")
    if not dc("ps", "--status", "running", "-q", "app", capture_output=True, text=True).stdout.strip():
        raise SystemExit("app no esta activa en este contexto Compose")
    carpeta = RAIZ / "backups" / datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    carpeta.mkdir(parents=True, mode=0o700)
    try:
        dc("stop", "app")
        # Todo /data: base, WAL, adjuntos y claves de firma.
        with (carpeta / "data.tar.gz").open("wb") as f:
            dc("run", "--rm", "--no-deps", "-T", "--user", "0", "--entrypoint", "tar", "app",
               "-czf", "-", "-C", "/data", ".", stdout=f)
        check_archive(carpeta / "data.tar.gz")
        for nombre in ["compose.yaml", "compose.smtp.yaml"]:
            if (RAIZ / nombre).is_file():
                (carpeta / nombre).write_bytes((RAIZ / nombre).read_bytes())
        meta = exportar_env(RAIZ, carpeta)
        escribir_manifiesto(carpeta, SOFTWARE, VERSION, DATABASE,
                            artefactos_presentes(carpeta), extra=meta)
    except Exception:
        marcar_fallido(carpeta, SOFTWARE, VERSION, DATABASE)
        raise
    finally:
        dc("start", "app")
    print("Respaldo completo:", carpeta)
    print("El .env no viaja en claro: solo env.vars y, si hay receptor age, env.age.")
    print("Contiene la boveda cifrada y las claves de firma: cifrar y copiar fuera del VPS.")
    return 0


if __name__ == "__main__":
    raise SystemExit(ejecutar(main))
