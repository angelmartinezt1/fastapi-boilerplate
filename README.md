# FastAPI + Lambda Handler - Guía para Principiantes

Este proyecto es un boilerplate de FastAPI con Python 3.11, preparado para desarrollo local y despliegue en AWS Lambda.

## 🚀 Configuración Inicial

### Prerrequisitos
- Python 3.11 instalado
- Git

### 1. Clonar o descargar el proyecto
```bash
git clone <url-del-repositorio>
cd mi-fastapi-project
```

### 2. Crear entorno virtual
```bash
python3.11 -m venv venv
```

### 3. Activar entorno virtual
```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**Nota**: Verás `(venv)` al inicio de tu terminal cuando esté activado.

### 4. Instalar dependencias

#### Para desarrollo local:
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### Solo para producción:
```bash
pip install -r requirements.txt
```

## 🛠️ Desarrollo Local

### Ejecutar el servidor de desarrollo
```bash
python app/local_server.py
```

**Alternativa usando uvicorn directamente:**
```bash
uvicorn app.main:app --reload
```

La aplicación estará disponible en:
- **API**: http://127.0.0.1:8000
- **Documentación**: http://127.0.0.1:8000/docs
- **Redoc**: http://127.0.0.1:8000/redoc

### Detener el servidor
Presiona `Ctrl + C` en la terminal.

## 📁 Estructura del Proyecto

```
mi-fastapi-project/
├── venv/                      # Entorno virtual (no subir a git)
├── app/
│   ├── __init__.py           # Hace de app un paquete Python
│   ├── main.py               # App factory
│   ├── lambda_handler.py     # Lambda entry point
│   └── local_server.py       # Local entry point
├── requirements.txt          # Dependencias generales del proyecto
├── requirements-dev.txt      # Dependencias para desarrollo local
├── requirements-lambda.txt   # Dependencias optimizadas para Lambda
├── .gitignore               # Archivos a ignorar en git
└── README.md                # Este archivo
```

## 🔧 Comandos Útiles

### Gestión del entorno virtual
```bash
# Activar entorno virtual
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Desactivar entorno virtual
deactivate
```

### Desarrollo
```bash
# Ejecutar servidor local (recomendado)
python app/local_server.py

# Ejecutar con uvicorn directamente
uvicorn app.main:app --reload

# Ejecutar en puerto específico
uvicorn app.main:app --reload --port 8080

# Ejecutar accesible desde otras máquinas
uvicorn app.main:app --reload --host 0.0.0.0
```

### Gestión de dependencias
```bash
# Instalar dependencias para desarrollo
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Instalar nueva dependencia general
pip install nombre-paquete
echo "nombre-paquete==version" >> requirements.txt

# Instalar dependencia solo para desarrollo
pip install nombre-paquete-dev
echo "nombre-paquete-dev==version" >> requirements-dev.txt

# Generar requirements automáticamente (opcional)
pip freeze > requirements-all.txt
```

## 📚 Endpoints Disponibles

- `GET /` - Endpoint de bienvenida
- `GET /health` - Verificación de salud de la API
- `GET /docs` - Documentación interactiva (Swagger UI)
- `GET /redoc` - Documentación alternativa (ReDoc)

## 🚀 Despliegue en AWS Lambda

Este proyecto usa una arquitectura separada para Lambda:

### Archivos de Lambda:
- **`app/lambda_handler.py`** - Entry point para AWS Lambda
- **`requirements-lambda.txt`** - Dependencias optimizadas para Lambda (sin uvicorn, etc.)

### Preparar para Lambda:
```bash
# Instalar solo dependencias de Lambda
pip install -r requirements-lambda.txt

# Crear package para Lambda
zip -r lambda-deployment.zip app/ -x "app/__pycache__/*"
```

### Configuración en AWS:
- **Handler**: `app.lambda_handler.handler`
- **Runtime**: Python 3.11
- **Timeout**: 30 segundos (ajustar según necesidad)

## 🤔 Resolución de Problemas Comunes

### "Command not found: python3.11"
- Asegúrate de tener Python 3.11 instalado
- En algunos sistemas, usa `python` en lugar de `python3.11`

### "Module not found"
- Verifica que el entorno virtual esté activado
- Reinstala las dependencias: `pip install -r requirements.txt`

### El servidor no se conecta
- Verifica que no haya otro proceso usando el puerto 8000
- Usa un puerto diferente: `uvicorn app.main:app --reload --port 8080`

## 📖 Recursos para Aprender

- [Documentación oficial de FastAPI](https://fastapi.tiangolo.com/)
- [Tutorial de FastAPI](https://fastapi.tiangolo.com/tutorial/)
- [Guía de Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)

## 🤝 Contribuir

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-feature`)
3. Commit tus cambios (`git commit -m 'Agregar nueva feature'`)
4. Push a la rama (`git push origin feature/nueva-feature`)
5. Abre un Pull Request

## 📝 Notas

- Nunca subas la carpeta `venv/` a git
- **Tres archivos de requirements**:
  - `requirements.txt` - Dependencias base necesarias en todos los entornos
  - `requirements-dev.txt` - Herramientas adicionales para desarrollo (pytest, black, etc.)
  - `requirements-lambda.txt` - Dependencias optimizadas para Lambda (sin uvicorn)
- Usa el entorno virtual para mantener las dependencias aisladas
- **Entry points separados**:
  - `app/local_server.py` para desarrollo local
  - `app/lambda_handler.py` para AWS Lambda
  - `app/main.py` contiene la app factory común