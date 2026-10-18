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

El compose principal (`compose.yaml`) ya cumple el contrato de Coolify: el servicio `app` no publica puertos propios (Traefik enruta el dominio), no usa `container_name`, ni poderes sobre el host, y Coolify asigna el nombre del proyecto y del volumen.

Para desplegar desde Coolify:

1. Crea la aplicación con build pack **Docker Compose** apuntando a `compose.yaml`.
2. Configura el dominio en Coolify (Traefik se encarga del TLS).
3. Define estas variables en la UI de Coolify:

   | Variable | Obligatoria | Default | Descripción |
   |---|---|---|---|
   | `VAULT_HOST` | sí | — | Dominio público (ej. `boveda.tudominio.cl`). Se usa como `DOMAIN: https://${VAULT_HOST}`. |
   | `OWNER_EMAIL` | sí | — | Correo del propietario. Único usuario que podrá crear organizaciones. |
   | `SIGNUPS_ALLOWED` | no | `false` | `true` solo durante el alta inicial privada; vuelve a `false` cuando crees la cuenta del propietario. |
   | `INVITATIONS_ALLOWED` | no | `false` | `true` únicamente si vas a configurar SMTP y permitir invitaciones de organización. |
   | `SMTP_HOST` | no | vacío | Si se deja vacío, no se envía correo y las invitaciones quedan inactivas aunque `INVITATIONS_ALLOWED=true`. |
   | `SMTP_PORT` | no | `587` | |
   | `SMTP_SECURITY` | no | `starttls` | |
   | `SMTP_FROM` | no | vacío | Remitente (ej. `boveda@tudominio.cl`). |
   | `SMTP_FROM_NAME` | no | `Hefesto Boveda` | |
   | `SMTP_USERNAME` | no | vacío | |
   | `SMTP_PASSWORD` | no | vacío | |
   | `SMTP_ACCEPT_INVALID_CERTS` | no | `false` | |
   | `SMTP_ACCEPT_INVALID_HOSTNAMES` | no | `false` | |
   | `SMTP_DEBUG` | no | `false` | |

4. **Alta privada inicial.** Antes de exponer el dominio público, pon `SIGNUPS_ALLOWED=true` en la UI, espera a que Vaultwarden reinicie, crea la cuenta con el correo `OWNER_EMAIL` y una contraseña maestra elegida por su titular, y vuelve a poner `SIGNUPS_ALLOWED=false`. El puerto del bootstrap (`compose.bootstrap.yaml`, `127.0.0.1:8091:80`) sirve solo para usar `python3 scripts/configure.py` + `docker compose` directos sobre el loopback del servidor; con Coolify no se usa ese override.

`scripts/configure.py` sigue siendo válido para `docker compose` directo (genera `VAULT_HOST` y `OWNER_EMAIL` en `.env`). Las variables `COMPOSE_PROJECT_NAME` y `VOLUME_PREFIX` que ese script dejaba en `.env` ya no las usa el compose; Coolify asigna esos nombres por sí mismo.

Comprueba que tu compose sigue cumpliendo el contrato Coolify después de cualquier cambio:

```sh
bash scripts/coolify-check.sh
```

El script genera un `.env` con valores ficticios no secretos, renderiza el compose con `docker compose config` y verifica que no queden `name:` fijos a nivel raíz ni en volúmenes, ni campos que den poder sobre el host en servicios sin profiles.
