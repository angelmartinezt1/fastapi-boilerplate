#!/usr/bin/env python3
"""
Test script para simular el comportamiento del Lambda Authorizer
"""
import requests
import json

BASE_URL = "http://localhost:8081"

def test_me_endpoint_with_headers():
    """Test endpoint /me con headers simulando Lambda Authorizer"""

    print("🧪 Testing /me endpoint with Lambda Authorizer context simulation")
    print("=" * 60)

    # Simular headers que API Gateway pasaría desde Lambda Authorizer
    headers = {
        "x-apigateway-user-id": "auth0|12345678901234567890",
        "x-apigateway-user-email": "user@example.com",
        "x-apigateway-access-type": "full",
        "x-apigateway-scope": "read:users write:users",
        "x-apigateway-current-store": "store_123",
        "x-apigateway-issuer": "https://dev.auth0.com/",
        "x-apigateway-azp": "client_app_id"
    }

    print("📤 Headers being sent:")
    for key, value in headers.items():
        print(f"  {key}: {value}")

    print("\n🔄 Making request to /me...")

    try:
        response = requests.get(f"{BASE_URL}/me", headers=headers)

        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Response:")
            print(json.dumps(data, indent=2))
        else:
            print("❌ Error response:")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on localhost:8081")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_me_endpoint_without_auth():
    """Test endpoint /me sin headers de autenticación"""

    print("\n🧪 Testing /me endpoint WITHOUT auth headers")
    print("=" * 60)

    print("🔄 Making request to /me without auth headers...")

    try:
        response = requests.get(f"{BASE_URL}/me")

        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Response (should show empty context in dev):")
            print(json.dumps(data, indent=2))
        else:
            print("❌ Error response:")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on localhost:8081")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_api_endpoint():
    """Test endpoint de API que requiere autenticación"""

    print("\n🧪 Testing /api/123/users endpoint (requires auth in Lambda)")
    print("=" * 60)

    headers = {
        "x-apigateway-user-id": "auth0|12345678901234567890",
        "x-apigateway-user-email": "user@example.com",
        "x-apigateway-access-type": "full"
    }

    try:
        response = requests.get(f"{BASE_URL}/api/123/users", headers=headers)

        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✅ Endpoint accessible (note: auth middleware skipped in dev)")
        else:
            print("❌ Error response:")
            print(response.text)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Lambda Authorizer Middleware Test")
    print("Note: In development environment, auth middleware is SKIPPED")
    print("This test shows how it would work in Lambda environment")

    test_me_endpoint_without_auth()
    test_me_endpoint_with_headers()
    test_api_endpoint()

    print("\n💡 Summary:")
    print("- In development: Auth middleware is skipped, endpoints work normally")
    print("- In Lambda: Auth middleware would enforce authentication for /api/* and /me")
    print("- Use headers x-apigateway-* to simulate Lambda Authorizer context")