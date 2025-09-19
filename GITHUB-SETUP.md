## 🚀 GitHub Setup (Environments, Variables & Secrets)

Este proyecto incluye un script para crear automáticamente **environments**, **variables** y **secrets** en GitHub Actions.

### 📂 Estructura

```
scripts/
├─ github-env.json     # Configuración de variables/secrets
└─ github-setup.sh     # Script de inicialización
```

---

### 🔑 Requisitos

1. **GitHub CLI (`gh`)**  
   En Fedora:
   ```bash
   sudo dnf install gh jq
   gh auth login
   ```
   > Selecciona **GitHub.com** → **HTTPS** y sigue las instrucciones para autenticarte.

2. **Variables de entorno para secrets**  
   Antes de ejecutar, exporta los valores que uses en `github-env.json`:
   ```bash
   export DB_PASSWORD="global-secret"
   export DB_PASSWORD_DEV="dev-secret"
   export DB_PASSWORD_PROD="prod-secret"
   ```
   Si cambiaste los nombres dentro de `${...}`, exporta esas variables.

---

### ⚙️ Configuración

Edita `scripts/github-env.json` para definir:
* Variables de **repo** (opcionales).
* Variables y secrets **por environment** (`development`, `production`, etc.).
* Puedes usar `${NOMBRE_VAR}` para que el script lea el valor de una variable de entorno.

Ejemplo abreviado:
```json
{
  "repo": { "variables": {} },
  "environments": [
    {
      "name": "development",
      "variables": {
        "AWS_REGION": "us-east-1",
        "AWS_ROLE_OIDC": "arn:aws:iam::123456789012:role/github-oidc-deploy-role-dev"
      },
      "secrets": {
        "DB_PASSWORD": "${DB_PASSWORD_DEV}"
      }
    },
    {
      "name": "production",
      "variables": {
        "AWS_REGION": "us-east-1",
        "AWS_ROLE_OIDC": "arn:aws:iam::123456789012:role/github-oidc-deploy-role-prod"
      },
      "secrets": {
        "DB_PASSWORD": "${DB_PASSWORD_PROD}"
      }
    }
  ]
}
```

---

### ▶️ Ejecución

Desde la raíz del proyecto:

```bash
chmod +x scripts/github-setup.sh
./scripts/github-setup.sh OWNER/REPO
```

Reemplaza `OWNER/REPO` por el repositorio de GitHub (por ejemplo `angelmartz/fastapi-sam`).

El script:

* Crea o actualiza los **environments** indicados.
* Crea/actualiza **variables** y **secrets** tanto a nivel de repo como por environment.
* Usa `gh` para cifrar los secrets automáticamente (no necesitas PyNaCl ni pasos extra).

---

### ✅ Verificación

Puedes comprobar los valores creados:

```bash
# Variables y secrets de environment production
gh variable list -R OWNER/REPO -e production
gh secret   list -R OWNER/REPO -e production

# Variables y secrets de environment development
gh variable list -R OWNER/REPO -e development
gh secret   list -R OWNER/REPO -e development
```

> 🔒 Los secrets nunca mostrarán su valor, solo el nombre.

---

Con este procedimiento tu repositorio quedará listo para que los **GitHub Actions** usen las variables y secrets de cada environment en los despliegues.