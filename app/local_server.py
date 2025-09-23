# app/local_server.py
"""
Servidor local para desarrollo
Ejecutar con: python app/local_server.py
"""
import os
import sys
import asyncio
from pathlib import Path
import uvicorn
from contextlib import asynccontextmanager

# ⬇️ Coloca la raíz del repo (padre de /app) como cwd y en sys.path
ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8081,
        reload=True,
        reload_dirs=["app"],
        log_level="info",
        # Esto ayuda a uvicorn a resolver la app desde la raíz correcta
        app_dir=str(ROOT),
        workers=1,  # evita sorpresas con múltiples workers en dev
    )
