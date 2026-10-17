# Respaldo, restauración y traspaso
## Respaldo con pausa
```sh
python3 scripts/backup.py
```
Usar Python 3.11+ y el mismo proyecto Compose del recurso. Se detiene app, se archiva TODO /data (SQLite + WAL correspondiente, adjuntos, claves y config.json si existe), se copian configuraciones del kit y se reinicia app. Después se valida el tar y PRAGMA quick_check en una copia privada de SQLite. El manifest completed se escribe solo si todo termina correctamente. No usar respaldos incompletos.

La pausa impide sincronizar cambios durante la ventana; avisar y comprobar sincronización posterior. No ejecutar el backup si otro contenedor/proceso escribe el mismo volumen. Se requiere espacio para el tar y una copia temporal de SQLite. El archivo se crea con permisos restrictivos, pero NO se cifra automáticamente. Puede contener metadatos y claves del servidor además de elementos cifrados.

Cifrar antes de copiar fuera del VPS mediante la herramienta corporativa (por ejemplo restic o age). Guardar clave de recuperación separada y ensayar descifrado. El ZIP no instala ni configura repositorio externo, cron o retención. Definirlos tras medir duración/espacio. Guardar también este kit y configuración DNS/proxy/SMTP externa.

## Recuperar en proyecto vacío
1. Recuperar kit y respaldo confiable, descifrarlo en un directorio privado. Los hashes detectan corrupción, no certifican la identidad del archivo.
2. Copiar .env y compose.yaml del respaldo al directorio destino; cambiar COMPOSE_PROJECT_NAME y VOLUME_PREFIX a nombres NUEVOS, ajustar VAULT_HOST/OWNER_EMAIL si corresponde. Conservar imagen de la misma versión. `chmod 600 .env`.
3. Ejecutar `docker compose pull`. NO arrancar app: crearía una base nueva.
4. Ejecutar `python3 scripts/restore.py /ruta/backup`. Valida hashes, rutas/tipos, SQLite y exige volumen vacío; no borra datos existentes. Rechaza enlaces del tar. Ante fallo parcial, usar otro volumen nuevo. No mezclar un db.sqlite3 con WAL de otro respaldo.
5. Revisar config.json heredado si existe; podría tener dominio y políticas distintas. Usar entorno aislado de prueba, sin SMTP ni acceso público hasta verificarlo. No imprimirlo en soporte.
6. Ejecutar `docker compose up -d`. Revisar salud y logs, ingresar con una cuenta de prueba, descifrar secreto ficticio, abrir adjunto y probar colección compartida/MFA. La prueba SQLite no demuestra que los usuarios pueden descifrar sus datos.
7. Para corte real: bloquear escrituras en origen, último respaldo, restauración en destino nuevo, verificación y cambio DNS. Mantener origen detenido. No volver a activar origen con datos antiguos después de nuevas escrituras en destino sin reconciliación.

## Actualización
Registrar versión de servidor y clientes. Revisar release notes, clonar/restaurar para pruebas y tomar respaldo completo antes de cambiar imagen/tag/digest. Las migraciones pueden ejecutarse al arrancar; rollback requiere copia y versión compatible, no solo bajar tag.

## Entrega
Inventario de dominio, DNS, proxy, proyecto, volumen, versión/digest, propietarios, SMTP, respaldos cifrados y prueba de restauración. Entregar accesos por gestor seguro y revocar los del proveedor saliente. Hefesto opera infraestructura; cada titular conserva su contraseña maestra. Acordar quién atiende incidentes, actualizaciones y salida de usuarios.
