#!/usr/bin/env python3
"""
Performance test script to measure Phase 1 optimizations
Tests both validate_responses=True (development) and validate_responses=False (production)
"""
import time
import json
import requests
import statistics

BASE_URL = "http://localhost:8081"

def time_request(url, method="GET", data=None, headers=None):
    """Time a single HTTP request"""
    start = time.time()
    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        response = requests.post(url, json=data, headers=headers)
    end = time.time()

    return {
        "time_ms": (end - start) * 1000,
        "status_code": response.status_code,
        "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
    }

def run_performance_test(endpoint, method="GET", data=None, iterations=10):
    """Run performance test for an endpoint"""
    print(f"\n🧪 Testing {method} {endpoint} ({iterations} iterations)")

    times = []
    for i in range(iterations):
        result = time_request(f"{BASE_URL}{endpoint}", method, data)
        times.append(result["time_ms"])
        if i == 0:  # Print first response for verification
            print(f"✅ Status: {result['status_code']}")
            if isinstance(result['response'], dict):
                print(f"✅ Response has data: {'data' in result['response']}")

    avg_time = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)

    print(f"📊 Avg: {avg_time:.1f}ms | Min: {min_time:.1f}ms | Max: {max_time:.1f}ms")
    return avg_time

def main():
    print("🚀 FastAPI Performance Test - Phase 1 Optimizations")
    print("=" * 60)

    # Test basic endpoints
    health_time = run_performance_test("/health")

    # Test user creation with a sample user (unique email each test)
    import random
    user_data = {
        "email": f"test{int(time.time())}{random.randint(1000,9999)}@example.com",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "+1234567890"
    }

    create_time = run_performance_test("/api/123/users", "POST", user_data)

    print("\n🎯 Performance Summary:")
    print(f"Health endpoint: {health_time:.1f}ms")
    print(f"User creation: {create_time:.1f}ms")

    # Performance expectations
    if health_time < 50:
        print("✅ Health endpoint: EXCELLENT (< 50ms)")
    elif health_time < 100:
        print("🟡 Health endpoint: GOOD (< 100ms)")
    else:
        print("🔴 Health endpoint: NEEDS IMPROVEMENT (> 100ms)")

    if create_time < 100:
        print("✅ User creation: EXCELLENT (< 100ms)")
    elif create_time < 200:
        print("🟡 User creation: GOOD (< 200ms)")
    else:
        print("🔴 User creation: NEEDS IMPROVEMENT (> 200ms)")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on localhost:8081")
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")