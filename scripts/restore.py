#!/usr/bin/env python3
"""Restauracion de la boveda en un destino nuevo y vacio.

Sin --confirmar CONFIRMAR_RESTAURACION no se escribe nada; con --dry-run se
simula. Valida manifiesto y sha256 antes de tocar el destino, exige el volumen
vacio y deja restore-report.json y auditoria.
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from archive_check import check_archive
from respaldo_contrato import (RespaldoError, auditar, ejecutar, ejecutar_check,
                               escribir_informe, opciones_restore)

SOFTWARE = "hefesto-boveda"
VERSION = "1.37.4"
DATABASE = "sqlite"
RAIZ = Path(__file__).resolve().parents[1]
os.chdir(RAIZ)
os.umask(0o077)


def dc(*a, **kw):
    return subprocess.run(["docker", "compose", *a], check=True, **kw)


def main():
    modo, origen = opciones_restore(sys.argv[1:])
    origen = Path(origen).resolve()
    ejecutar_check(str(origen), SOFTWARE, VERSION, DATABASE)
    check_archive(origen / "data.tar.gz")
    if modo == "dry-run":
        print("Simulacion: el respaldo es integro y no se escribio nada.")
        print("Para restaurar de verdad: --confirmar CONFIRMAR_RESTAURACION")
        return 0
    if dc("ps", "--status", "running", "-q", "app", capture_output=True, text=True).stdout.strip():
        raise RespaldoError("app esta activa en el destino; detenerla antes de restaurar", 5)
    if not (RAIZ / ".env").is_file():
        raise RespaldoError("Preparar el .env del destino segun docs/operacion.md "
                            "(no viaja en el respaldo)", 5)
    ocupado = dc("run", "--rm", "--no-deps", "-T", "--user", "0", "--entrypoint", "find", "app",
                 "/data", "-mindepth", "1", "-maxdepth", "1",
                 capture_output=True, text=True).stdout.strip()
    if ocupado:
        raise RespaldoError("Volumen no vacio; no se sobrescribe", 5)
    with (origen / "data.tar.gz").open("rb") as f:
        dc("run", "--rm", "--no-deps", "-T", "--user", "0", "--entrypoint", "tar", "app",
           "-xzf", "-", "-C", "/data", stdin=f)
    escribir_informe(origen, software=SOFTWARE, version=VERSION, database=DATABASE,
                     modo="confirmado", resultado="restaurado", destino=str(RAIZ))
    auditar(RAIZ, operacion="restore", kit=SOFTWARE, origen=str(origen), destino=str(RAIZ),
            resultado="restaurado")
    print("Restaurado. Revisar configuracion heredada y arrancar app; realizar aceptacion.")
    print("Ante fallo parcial usar un volumen nuevo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(ejecutar(main))
