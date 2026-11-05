# Publicar un proyecto independiente

Nombre sugerido: `simpleLinuxClipboardForWayland`.
Crea un repositorio vacío en tu cuenta de GitHub, sin README ni licencia
automáticos: estos archivos ya se revisan aquí. No se ha creado ni publicado
ningún repositorio remoto desde esta sesión.

Se conserva la historia del proyecto original. En esta copia su remoto se
llama `upstream`; la rama local ya no sigue la rama X11. El repositorio nuevo
tendrá el nombre `origin`:

```bash
git remote -v
git remote add origin git@github.com:FORDDIVEN/simpleLinuxClipboardForWayland.git
git add .
git diff --cached --stat
git commit -m "Prepare independent GNOME Wayland project"
git push -u origin main
```

Sustituye la cuenta o el nombre si elegiste otros. Revisa los cambios antes
del commit. `.gitignore` excluye entornos virtuales, compilaciones, paquetes,
cachés y el archivo local; sí incluye fuentes de empaquetado y pruebas.

Sube los `.deb` y sus checksums como adjuntos de una GitHub Release; no los
añadas al código fuente. Publica únicamente la versión que quieras ofrecer
para pruebas y describe su estado experimental. Los paquetes generados antes
de esta reorganización siguen siendo utilizables, pero incluyen la
estructura de documentación anterior. Una nueva compilación incorporará
las rutas y documentos actuales.

Elige una licencia explícita antes de presentar el proyecto como software con
licencia estándar. Consulta [ORIGIN.md](../ORIGIN.md); no se ha inferido ni
asignado una licencia sin decisión del titular.
