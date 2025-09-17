"""
Servidor local para desarrollo
Ejecutar con: python app/local_server.py
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",  # Import string para permitir reload
        host="127.0.0.1",
        port=8081,
        reload=True,  # Recarga automática en desarrollo
        reload_dirs=["app"],  # Solo observar cambios en la carpeta app
        log_level="info"
    )