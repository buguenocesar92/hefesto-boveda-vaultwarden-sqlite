# Servicio Hefesto y migración
Oferta: instalación aislada por empresa, organización de colecciones, capacitación, respaldo cifrado y mantenimiento mensual. Dirigido a equipos que comparten accesos laborales. Cotizar según usuarios, adjuntos, soporte, infraestructura y horario de atención. No venderlo como producto oficial Bitwarden ni prometer certificaciones o características no verificadas.

Piloto: dos usuarios nominales, una organización, dos colecciones, MFA y solo credenciales ficticias. Validar permisos, sincronización, incorporación/salida y restauración antes de guardar accesos reales. La matriz CSV es plantilla de planificación; no se importa automáticamente.

## Desde otro gestor
Inventariar formatos soportados por el cliente y versión actuales; probar importación de pocos elementos ficticios. Preferir exportación cifrada compatible cuando exista. Algunos formatos exportan secretos en texto claro: limitar su acceso, no subirlos a este chat/Git/almacenamiento público y eliminarlos conforme a la política del dispositivo tras verificar el destino. Importar puede duplicar elementos.

La exportación de una bóveda personal no equivale al respaldo del servidor ni necesariamente incluye adjuntos, organizaciones y todas las propiedades. Exportar organizaciones con permisos adecuados; conciliar conteos, URIs, campos, TOTP y adjuntos. Verificar manualmente los elementos críticos antes de cerrar el origen.

## Hacia otro proveedor
Transferir el respaldo completo a otra instancia Vaultwarden de versión compatible siguiendo operacion.md. Para cambiar a otro gestor, utilizar exportaciones admitidas y probar pérdida de campos/adjuntos, MFA y permisos. El archivo SQLite no es una base importable directamente en Bitwarden oficial ni Odoo.

Odoo puede gestionar clientes, contratos y soporte de este servicio; no es el destino de las contraseñas de la bóveda. No hay integración automática Odoo/Supabase ni sincronización de secretos en este kit.

## Operación con equipos
Revocar accesos cuando una persona sale y rotar las credenciales compartidas que conocía; eliminar acceso a la colección no hace que olvide una contraseña copiada. Acordar acceso de emergencia/recuperación antes de habilitarlo y probar sus efectos. Mantener contraseñas maestras y códigos de recuperación bajo control de sus titulares. No prometer que soporte puede descifrar cualquier bóveda olvidada.
