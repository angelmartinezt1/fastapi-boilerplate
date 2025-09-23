# Lambda Authorizer Middleware

## Descripción

El middleware `LambdaAuthorizerMiddleware` procesa automáticamente el contexto del Lambda Authorizer en entorno AWS Lambda, proporcionando autenticación y autorización para endpoints protegidos.

## Funcionamiento

### Detección de Entorno
- **Desarrollo Local**: El middleware se omite automáticamente cuando `app_config.is_lambda = False`
- **AWS Lambda**: Se activa automáticamente cuando detecta el entorno Lambda

### Rutas Protegidas
El middleware protege automáticamente:
- `/api/*` - Todas las rutas de API
- `/me` - Endpoint de perfil de usuario

### Rutas Excluidas (Públicas)
- `/health` - Health check
- `/docs` - Documentación Swagger
- `/openapi.json` - OpenAPI schema
- `/redoc` - ReDoc documentation

## Extracción de Contexto

El middleware extrae el contexto del Lambda Authorizer desde múltiples fuentes:

### 1. Evento de API Gateway (Preferido)
```javascript
// Estructura esperada en el evento Lambda
{
  "requestContext": {
    "authorizer": {
      "lambda": {
        "sub": "auth0|12345678901234567890",
        "email": "user@example.com",
        "accessType": "full",
        "scope": "read:users write:users",
        "current_store": "store_123",
        "iss": "https://dev.auth0.com/",
        "azp": "client_app_id"
      }
    }
  }
}
```

### 2. Headers Personalizados (Fallback)
```http
x-apigateway-user-id: auth0|12345678901234567890
x-apigateway-user-email: user@example.com
x-apigateway-access-type: full
x-apigateway-scope: read:users write:users
x-apigateway-current-store: store_123
x-apigateway-issuer: https://dev.auth0.com/
x-apigateway-azp: client_app_id
```

## Validación de Contexto

### Campos Requeridos
- `sub`: Subject ID del usuario (requerido)
- `email`: Email del usuario (requerido, debe contener @)

### Respuestas de Error

#### 401 - Authentication Required
```json
{
  "metadata": {
    "success": false,
    "message": "Authentication required",
    "timestamp": null
  },
  "errors": [{
    "field": "authorization",
    "message": "Missing or invalid authorization context"
  }]
}
```

#### 403 - Access Forbidden
```json
{
  "metadata": {
    "success": false,
    "message": "Access forbidden",
    "timestamp": null
  },
  "errors": [{
    "field": "authorization",
    "message": "Missing required field: sub"
  }]
}
```

## Uso en Endpoints

### Endpoint /me
```python
from fastapi import Request
from app.middleware.auth import get_auth_context, get_current_user_id

@router.get("/me")
async def get_me(request: Request):
    # Obtener contexto completo
    auth_context = get_auth_context(request)

    # Obtener campos específicos
    user_id = get_current_user_id(request)
    user_email = get_current_user_email(request)
    current_store = get_current_store(request)

    return {
        "user_id": user_id,
        "email": user_email,
        "current_store": current_store,
        "full_context": auth_context
    }
```

### Helpers Disponibles
- `get_auth_context(request)` - Contexto completo del authorizer
- `get_current_user_id(request)` - ID del usuario (sub)
- `get_current_user_email(request)` - Email del usuario
- `get_current_store(request)` - Tienda actual

### Acceso Directo al Estado
```python
# Disponible en request.state después del middleware
user_id = request.state.user_id
user_email = request.state.user_email
current_store = request.state.current_store
access_type = request.state.access_type
scope = request.state.scope
```

## Configuración del Lambda Authorizer

### Ejemplo de Lambda Authorizer Function
```javascript
exports.handler = async (event) => {
  // Validar token JWT
  const decodedToken = validateJWT(event.authorizationToken);

  return {
    principalId: decodedToken.sub,
    policyDocument: {
      Version: '2012-10-17',
      Statement: [{
        Action: 'execute-api:Invoke',
        Effect: 'Allow',
        Resource: event.methodArn
      }]
    },
    context: {
      accessType: 'full',
      scope: decodedToken.scope,
      email: decodedToken.email,
      iss: decodedToken.iss,
      sub: decodedToken.sub,
      azp: decodedToken.azp,
      current_store: decodedToken.current_store || null
    }
  };
};
```

### SAM Template Configuration
```yaml
ApiGatewayApi:
  Type: AWS::ApiGatewayV2::Api
  Properties:
    Name: !Sub "${AWS::StackName}-api"
    ProtocolType: HTTP

LambdaAuthorizer:
  Type: AWS::ApiGatewayV2::Authorizer
  Properties:
    ApiId: !Ref ApiGatewayApi
    AuthorizerType: REQUEST
    AuthorizerUri: !Sub "arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${AuthorizerFunction.Arn}/invocations"
    Name: JwtAuthorizer

ProtectedRoute:
  Type: AWS::ApiGatewayV2::Route
  Properties:
    ApiId: !Ref ApiGatewayApi
    RouteKey: "GET /api/{proxy+}"
    AuthorizationType: CUSTOM
    AuthorizerId: !Ref LambdaAuthorizer
    Target: !Sub "integrations/${LambdaIntegration}"
```

## Testing

### Desarrollo Local
El middleware se omite automáticamente. Usar el script de prueba:
```bash
python test_lambda_auth.py
```

### Testing en Lambda
Deploy el stack y hacer requests a los endpoints protegidos. El middleware procesará automáticamente el contexto del authorizer.

## Logging

El middleware registra automáticamente:
- ✅ Validación exitosa del contexto
- ⚠️ Contexto faltante o inválido
- ❌ Errores de extracción del contexto

```json
{
  "level": "INFO",
  "message": "Lambda authorizer context validated",
  "extra_data": {
    "path": "/api/123/users",
    "method": "GET",
    "user_id": "auth0|12345678901234567890",
    "email": "user@example.com",
    "access_type": "full"
  }
}
```