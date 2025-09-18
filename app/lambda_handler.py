"""
Handler para AWS Lambda
Configurar en Lambda: app.lambda_handler.handler
"""

from mangum import Mangum
from app.main import create_app

# Crear la aplicación FastAPI
app = create_app()

# Crear el handler para Lambda usando Mangum
handler = Mangum(app, lifespan="off")


# Opcional: Handler personalizado para casos específicos
def lambda_handler(event, context):
    """
    Handler alternativo con logging personalizado para Lambda
    """
    print(f"Event: {event}")
    print(f"Context: {context}")

    # Usar Mangum para manejar la request
    return handler(event, context)
