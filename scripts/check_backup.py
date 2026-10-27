#!/usr/bin/env python3
"""Verificacion de integridad de un respaldo de hefesto-boveda.

Codigos de salida: 0 integro, 1 uso, 2 integridad o manifiesto invalido,
4 material sensible en claro dentro del respaldo.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from archive_check import check_archive
from respaldo_contrato import ejecutar, ejecutar_check

SOFTWARE = "hefesto-boveda"
VERSION = "1.37.4"
DATABASE = "sqlite"


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python3 scripts/check_backup.py /ruta/respaldo")
    carpeta = sys.argv[1]
    ejecutar_check(carpeta, SOFTWARE, VERSION, DATABASE)
    check_archive(Path(carpeta) / "data.tar.gz")
    print("Manifiesto, checksums, SQLite y ausencia de secretos en claro verificados.")
    print("Esto no demuestra la recuperacion funcional de la boveda: falta el ensayo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(ejecutar(main))
