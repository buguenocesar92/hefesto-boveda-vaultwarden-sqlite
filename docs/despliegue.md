# Coolify y configuración del equipo
1. Un despliegue por empresa: dominio, proyecto Compose y volumen únicos. Crear el propietario en el inicio privado del README. No compartir su contraseña maestra con Hefesto. Crear una organización de prueba y una colección con un secreto ficticio.
2. Cerrar el registro antes de publicar:
```sh
docker compose -f compose.yaml up -d --force-recreate app
```
Esto elimina el puerto localhost:8091 y aplica DOMAIN con HTTPS. Comprobar que el registro no funciona; no basta que se oculte el botón. SIGNUPS_DOMAINS_WHITELIST debe seguir vacío, pues una whitelist puede alterar las restricciones de registro.
3. En Coolify cargar este directorio como recurso Compose y las variables .env. Asociar HTTPS al servicio app, puerto interno 80. Preservar Host y permitir WebSocket. No se requiere publicar el antiguo puerto 3012. No desplegar compose.bootstrap.yaml en el recurso público.
4. Si el alta se hizo en el mismo VPS fuera de Coolify, mantener VOLUME_PREFIX y detener el recurso anterior antes de iniciar el nuevo. Nunca dos instancias escribiendo el mismo SQLite. Los scripts deben usar el directorio/proyecto Compose que realmente ejecuta el servicio; revisar COMPOSE_PROJECT_NAME antes de operarlos.
5. Abrir el dominio HTTPS y verificar login/crear/editar/sincronizar un secreto ficticio. Configurar la URL de servidor propio en extensiones y apps compatibles antes de iniciar sesión. Anotar versiones de clientes probadas: no se garantiza compatibilidad con toda versión futura.
6. Activar TOTP y, si el cliente lo soporta, una llave de seguridad. Guardar códigos de recuperación fuera de la bóveda y probarlos con cuenta de ensayo. Registrar passkeys/WebAuthn solo en el dominio HTTPS definitivo; el origen forma parte de esas credenciales.
7. Definir organización, colecciones y permisos. Agregar segundo propietario de continuidad y usuarios nominales una vez habilitadas invitaciones. Probar aceptación/confirmación y acceso de cada rol. No usar una cuenta compartida de empresa para todos.

## SMTP e invitaciones
Agregar a .env SMTP_HOST, SMTP_PORT (587 por defecto), SMTP_SECURITY (starttls), SMTP_FROM, SMTP_USERNAME y SMTP_PASSWORD del proveedor autorizado. Guardar valores con comillas simples en .env; para claves con comillas especiales usar el gestor de secretos del despliegue y comprobar el parseo sin imprimirlas. Nunca desactivar validación de certificados.
```sh
docker compose -f compose.yaml -f compose.smtp.yaml up -d
```
Seleccionar ambos archivos en el despliegue permanente de Coolify y conservar variables en su gestor. compose.smtp.yaml habilita INVITATIONS_ALLOWED pero mantiene SIGNUPS_ALLOWED=false. Probar una invitación autorizada, aceptación y confirmación de miembro. No se ha enviado ningún correo. El paquete básico no tiene SMTP ni invitaciones.

## Panel global y configuración heredada
No se define ADMIN_TOKEN; /admin debe permanecer deshabilitado. DISABLE_ADMIN_TOKEN=false NO habilita un panel sin contraseña. No cambiarlo a true. Las tareas de organización se realizan desde el usuario propietario.
Si se importa un volumen que contiene config.json, sus valores pueden prevalecer sobre el entorno. Revisarlo localmente sin exponer secretos y reconciliar dominio, registro, invitaciones y admin antes de publicar. Este kit no crea config.json ni lo borra automáticamente. Un cambio de env no demuestra que una configuración heredada cambió.

## Funciones fuera de alcance inicial
Send, acceso de emergencia y notificaciones push requieren decisión/configuración adicional. No ofrecer SSO empresarial, recuperación universal de contraseñas, auditoría certificada o SLA sin implantación y validación específicas. Respaldar servidores no permite recuperar automáticamente una contraseña maestra olvidada.
