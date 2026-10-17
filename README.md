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
