# Política de tratamiento de datos personales — Boveda de contrasenas (Hefesto Studio)

Estado: vigente desde 2026-10-20. Responsable del tratamiento: el cliente que
opera el kit. Este documento describe qué datos guarda el kit, por qué, cuánto
tiempo los retiene y cómo se exercise los derechos del titular (Ley 21.719).

## 1. Qué datos guarda este kit

El kit de boveda (Vaultwarden) guarda, por persona usuaria:

- **Cuentas**: correo, hash de la contrasena maestra y ajustes de la cuenta.
- **Cofres**: el nombre del cofre y, dentro de el, el nombre de usuario, la
  contrasena, la URL, notas y archivos adjuntos de cada entrada. El contenido
  viaja cifrado con la contrasena maestra del usuario.
- **Organizaciones y colecciones**: pertenencias, roles y permisos.
- **Sesiones y tokens de refresco**: dispositivo, IP y fecha de la sesion.
- **Claves de firma del servidor**: el par de claves que firma las invitations
  y los enlaces del kit.
- **Copias locales de respaldo**: `backups/<timestamp>/` con el volumen `/data`
  completo (`data.tar.gz`), que incluye la base SQLite, su WAL y las claves de
  firma.

Una boveda de contrasenas es el repositorio de secretos de una persona: el
titular de los datos es el propio usuario de la boveda.

## 2. Qué datos NO guarda este kit

- El `.env` **no** se copia en claro al respaldo: solo sus nombres de
  variable (`env.vars`) y, si hay un receptor `age` configurado, el `.env`
  cifrado (`env.age`). Ver `docs/CONTRATO-RESPALDO.md`, regla 5.
- El kit no descifra los cofres: la contrasena maestra nunca se guarda, solo
  su hash, y el contenido de cada entrada sigue cifrado en la base.
- El kit no registra las contrasenas en los logs ni en los mensajes de error.
- El kit no envia las entradas a servicios de terceros.

## 3. Base legal y deberes

- **Minimización**: el kit guarda lo indispensable para cifrar el cofre del usuario. No
  guarda la contrasena maestra ni su derivacion, ni metadatos del navegador,
  ni el historial de escritura de cada entrada.
- **Finalidad**: guardar y sincronizar las credenciales del cliente. Los datos no se usan para otros fines ni se ceden a terceros.
- **Seguridad**: los respaldos se cifran en reposo con `age` hacia el destino del operador, la clave privada no está en este servidor, el `.env` nunca sale en claro y el contenido de los cofres sigue cifrado con AES.
- **Auditoría**: cada respaldo y cada restauración dejan registro en `logs/restore.log` con origen, sha256 verificado, destino y resultado. Es registro de actividades de tratamiento: no guarda valores de secretos, ni contrasenas, ni nombres de entrada.

## 4. Retención

| Dato | Dónde | Retención por defecto | Quién lo borra |
|---|---|---|---|
| Cuentas y sesiones | volumen `data` (SQLite) | mientras el cliente mantenga la cuenta | el operador, desde la interfaz |
| Cofres y entradas | volumen `data` (cifrados) | mientras el cliente los mantenga | el operador |
| Claves de firma del servidor | volumen `data` | mientras el kit este en uso; rotar si se sospecha uso indebido | el operador |
| Respaldos en disco | `backups/<timestamp>/` | **a definir por el operador**; el kit no borra nada por su cuenta | el operador |
| Registro de auditoría | `logs/restore.log` | append-only; se trunca por política del cliente | el operador |

**El kit no borra respaldos ni datos por su cuenta.** Borrar es una decisión del
operador, porque un respaldo borrado no se recupera.

## 5. Derechos del titular (acceso, rectificación y supresión)

El cliente que opera el kit debe poder atender las solicitudes de los
titulares (los usuarios de la boveda):

1. **Acceso**: el usuario abre su cofre con su contrasena maestra; el
   operador puede entregar el contenido descifrado solo cuando el titular lo
   pide, en un entorno controlado.
2. **Rectificación**: el usuario edita la entrada desde el cliente; el
   operador puede corregir datos de la cuenta (correo, ajustes) desde la
   interfaz.
3. **Supresión**: eliminar la cuenta y el cofre desde el cliente, y eliminar
   los respaldos que los contengan, dejando constancia en el registro de
   auditoria.
4. **Revocación del consentimiento**: cerrar sesiones y revocar tokens desde
   la cuenta del usuario.

El kit garantiza que los datos son localizables, corregibles y borrables; el
operador nunca necesita conocer la contrasena maestra para hacerlo.

## 6. Verificación

- `bats tests/backup_restore.bats` comprueba, con datos sintéticos, que el
  `.env` no queda en claro, que el manifiesto lleva las cinco claves, que la
  base SQLite del tar es integra, que un artefacto alterado se rechaza y que
  un destino no vacío aborta la restauración.
- `gitleaks` corre en CI sobre el repositorio y su historial.
