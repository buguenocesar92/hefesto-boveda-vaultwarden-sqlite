# Hefesto Bóveda · Vaultwarden
Kit para desplegar Vaultwarden 1.37.4 con SQLite y clientes compatibles con Bitwarden. Imagen publicada por el proyecto Vaultwarden y fijada por digest. Vaultwarden es una implementación independiente, no el servidor oficial de Bitwarden ni un servicio afiliado a esa empresa.

Incluye Compose para Coolify, alta inicial privada, SMTP opcional, respaldo del volumen completo, restauración a destino vacío, comprobación SQLite y documentación para equipos. Funciones nativas: bóveda personal, organizaciones, colecciones, compartir credenciales y autenticación de dos factores según clientes compatibles.

## Inicio privado
Requiere Linux, Docker Engine + Compose v2, Python 3.11+, dominio y proxy HTTPS. El tamaño depende de usuarios y adjuntos; medir en piloto antes de fijar capacidad contractual.
```sh
python3 scripts/configure.py cliente-demo boveda.tudominio.cl propietario@tudominio.cl
docker compose -f compose.yaml -f compose.bootstrap.yaml up -d
```
Desde el computador:
```sh
ssh -L 8091:127.0.0.1:8091 usuario@servidor
```
Abrir http://localhost:8091 (localhost es un contexto seguro del navegador). Crear la cuenta del correo OWNER_EMAIL con una contraseña maestra elegida por su titular. No hay contraseña predeterminada. No introducir credenciales reales hasta completar HTTPS y aceptación.

El alta privada permite registro solo mientras el override está activo y el puerto está limitado al loopback. No crear dominio público de Coolify todavía. Seguir docs/despliegue.md para cerrar el registro y publicar con HTTPS.

## Stack y límites
SQLite guarda datos en /data, junto con adjuntos y claves del servidor. Esta modalidad no requiere Supabase. Vaultwarden también admite PostgreSQL, pero este paquete no configura Supabase ni migra SQLite a PostgreSQL. Cambiar DATABASE_URL sin migración no traslada los datos. Supabase Auth y Storage no forman parte del producto.

Por defecto: registro público cerrado; invitaciones cerradas; panel global /admin sin habilitar; Send, acceso de emergencia, descarga de iconos y push móvil desactivados. SMTP opcional permite abrir invitaciones de organización de forma controlada. El usuario OWNER_EMAIL puede crear organizaciones; no obtiene por ello acceso a las bóvedas personales de otras cuentas.

Estado: archivos revisados estáticamente y validador de archivos ensayado con SQLite sintético. No se ha desplegado, conectado SMTP, probado clientes reales ni restaurado una instancia de producción. Ver docs/aceptacion.md. El ZIP no contiene contraseñas de usuarios ni imágenes Docker; estas se descargan al desplegar.

## Despliegue en Coolify (MVP Hefesto)

El compose principal (`compose.yaml`) ya cumple el contrato de Coolify: el servicio `app` no publica puertos propios (Traefik enruta el dominio), no usa `container_name`, ni poderes sobre el host, y Coolify asigna el nombre del proyecto.

Para desplegar desde Coolify:

1. Crea la aplicación en Coolify con build pack **Docker Compose** apuntando a `compose.yaml`. **No asignes el dominio público todavía**: la cuenta del propietario se crea antes de publicar la URL, para no exponer el formulario de registro mientras está abierto.

2. Define las variables mínimas en la UI de Coolify. Las claves con valor vacío (`SMTP_HOST`, `SMTP_FROM`, `SMTP_USERNAME`, `SMTP_PASSWORD`) se omiten al renderizar y no llegan al contenedor; defínelas solo cuando vayas a configurar correo.

   | Variable | Obligatoria | Default | Descripción |
   |---|---|---|---|
   | `VAULT_HOST` | sí | — | Dominio público final (ej. `boveda.tudominio.cl`). Se usa como `DOMAIN: https://${VAULT_HOST}`. |
   | `OWNER_EMAIL` | sí | — | Correo del propietario. Único usuario que podrá crear organizaciones. |
   | `SIGNUPS_ALLOWED` | no | `false` | `true` solo durante el alta inicial privada; vuelve a `false` cuando crees la cuenta del propietario. |
   | `INVITATIONS_ALLOWED` | no | `false` | `true` únicamente si vas a configurar SMTP y permitir invitaciones de organización. |
   | `SMTP_HOST` | no | (no se pasa) | Host SMTP. Si se deja vacío, no se envía correo y las invitaciones quedan inactivas aunque `INVITATIONS_ALLOWED=true`. |
   | `SMTP_PORT` | no | `587` | |
   | `SMTP_SECURITY` | no | `starttls` | |
   | `SMTP_FROM` | no | (no se pasa) | Remitente (ej. `boveda@tudominio.cl`). |
   | `SMTP_FROM_NAME` | no | `Hefesto Boveda` | |
   | `SMTP_USERNAME` | no | (no se pasa) | |
   | `SMTP_PASSWORD` | no | (no se pasa) | |
   | `SMTP_ACCEPT_INVALID_CERTS` | no | `false` | |
   | `SMTP_ACCEPT_INVALID_HOSTNAMES` | no | `false` | |
   | `SMTP_DEBUG` | no | `false` | |

3. **Alta privada inicial antes del dominio público.** Con `SIGNUPS_ALLOWED=true` ya definido, crea la cuenta por el camino del bootstrap (loopback del servidor), sin pasar por la URL pública:

   ```sh
   ssh usuario@servidor
   cd /ruta/al/repo
   docker compose -f compose.yaml -f compose.bootstrap.yaml up -d
   ```

   Desde tu computador, abre el puerto por SSH y entra al formulario:

   ```sh
   ssh -L 8091:127.0.0.1:8091 usuario@servidor
   ```

   Abre http://localhost:8091 (contexto seguro del navegador), registra la cuenta con el correo `OWNER_EMAIL` y una contraseña maestra elegida por su titular. Cuando termines, baja el stack de bootstrap (`docker compose down`) para liberar el puerto.

4. Vuelve a poner `SIGNUPS_ALLOWED=false` en la UI de Coolify y redespliega. Confirma en los logs que la variable quedó en `false` antes de seguir.

5. Asigna el dominio público en Coolify (Traefik se encarga del TLS). Solo después de este paso la bóveda queda accesible desde Internet.

`scripts/configure.py` sigue siendo válido para `docker compose` directo (genera `VAULT_HOST`, `OWNER_EMAIL`, `COMPOSE_PROJECT_NAME` y `VOLUME_PREFIX` en `.env`). El compose ya no fuerza `COMPOSE_PROJECT_NAME`: `docker compose` la sigue leyendo del `.env` si está definida, y Coolify asigna el nombre del proyecto por sí mismo. `VOLUME_PREFIX` se usa para nombrar el volumen `data` con un valor por defecto (`hefesto-boveda-data`); cambiarla crea un volumen nuevo y debe coordinarse con `scripts/backup.py` y `scripts/restore.py`, que apuntan a ese nombre.

Comprueba que tu compose sigue cumpliendo el contrato Coolify después de cualquier cambio:

```sh
bash scripts/coolify-check.sh
```

El script genera un `.env` con valores ficticios no secretos, renderiza el compose con `docker compose config` y verifica que no queden `name:` fijos a nivel raíz ni en redes, que los volúmenes parametrizados con `${VOLUME_PREFIX:-...}` lleven valor por defecto, que ningún bind exponga rutas fuera del repo y que no haya campos que den poder sobre el host en servicios sin profiles.
