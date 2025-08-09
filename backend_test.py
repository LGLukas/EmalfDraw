#!/usr/bin/env python3
"""
EmalfDraw Backend API Test Suite
Tests all backend API endpoints for the drawing ideas application
"""

import requests
import json
import os
from datetime import datetime
import time

# Get backend URL from frontend .env file
def get_backend_url():
    """Read the backend URL from frontend .env file"""
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading frontend .env: {e}")
        return None

# Configuration
BACKEND_URL = get_backend_url()
if not BACKEND_URL:
    print("ERROR: Could not find REACT_APP_BACKEND_URL in frontend/.env")
    exit(1)

API_BASE = f"{BACKEND_URL}/api"
print(f"Testing backend at: {API_BASE}")

# Test data
TEST_IDEA = "Draw a unicorn riding a bicycle"
DUPLICATE_IDEA = "Draw a cat wearing a wizard hat"  # This should exist in default ideas

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def log_pass(self, test_name):
        print(f"✅ PASS: {test_name}")
        self.passed += 1
    
    def log_fail(self, test_name, error):
        print(f"❌ FAIL: {test_name} - {error}")
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY: {self.passed}/{total} tests passed")
        if self.errors:
            print(f"\nFAILED TESTS:")
            for error in self.errors:
                print(f"  - {error}")
        print(f"{'='*60}")
        return self.failed == 0

def test_health_endpoint():
    """Test GET /api/health endpoint"""
    print("\n🔍 Testing Health Check Endpoint...")
    results = TestResults()
    
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        
        # Test status code
        if response.status_code == 200:
            results.log_pass("Health endpoint returns 200")
        else:
            results.log_fail("Health endpoint status code", f"Expected 200, got {response.status_code}")
        
        # Test response structure
        try:
            data = response.json()
            required_fields = ["status", "database", "ideas_count"]
            
            for field in required_fields:
                if field in data:
                    results.log_pass(f"Health response contains '{field}'")
                else:
                    results.log_fail(f"Health response missing field", f"Missing '{field}'")
            
            # Test specific values
            if data.get("status") == "healthy":
                results.log_pass("Health status is 'healthy'")
            else:
                results.log_fail("Health status", f"Expected 'healthy', got '{data.get('status')}'")
            
            if data.get("database") == "connected":
                results.log_pass("Database status is 'connected'")
            else:
                results.log_fail("Database status", f"Expected 'connected', got '{data.get('database')}'")
            
            # Check ideas count (should be 20 default ideas)
            ideas_count = data.get("ideas_count", 0)
            if ideas_count >= 20:
                results.log_pass(f"Ideas count is {ideas_count} (seeding worked)")
            else:
                results.log_fail("Ideas count", f"Expected >= 20, got {ideas_count}")
                
        except json.JSONDecodeError:
            results.log_fail("Health response format", "Invalid JSON response")
            
    except requests.exceptions.RequestException as e:
        results.log_fail("Health endpoint connection", str(e))
    
    return results.summary()

def test_get_all_ideas():
    """Test GET /api/ideas endpoint"""
    print("\n🔍 Testing Get All Ideas Endpoint...")
    results = TestResults()
    
    try:
        response = requests.get(f"{API_BASE}/ideas", timeout=10)
        
        # Test status code
        if response.status_code == 200:
            results.log_pass("Get ideas endpoint returns 200")
        else:
            results.log_fail("Get ideas status code", f"Expected 200, got {response.status_code}")
            return results.summary()
        
        # Test response structure
        try:
            data = response.json()
            
            if isinstance(data, list):
                results.log_pass("Response is a list")
            else:
                results.log_fail("Response format", "Expected list, got " + type(data).__name__)
                return results.summary()
            
            # Test we have default ideas
            if len(data) >= 20:
                results.log_pass(f"Found {len(data)} ideas (includes default ideas)")
            else:
                results.log_fail("Ideas count", f"Expected >= 20 ideas, got {len(data)}")
            
            # Test idea structure
            if data:
                idea = data[0]
                required_fields = ["id", "text", "created_at", "user_submitted"]
                
                for field in required_fields:
                    if field in idea:
                        results.log_pass(f"Idea object contains '{field}'")
                    else:
                        results.log_fail(f"Idea object missing field", f"Missing '{field}'")
                
                # Test specific default idea exists
                default_ideas_texts = [idea["text"] for idea in data]
                if "Draw a cat wearing a wizard hat" in default_ideas_texts:
                    results.log_pass("Default idea 'Draw a cat wearing a wizard hat' found")
                else:
                    results.log_fail("Default ideas", "Expected default idea not found")
                    
        except json.JSONDecodeError:
            results.log_fail("Get ideas response format", "Invalid JSON response")
            
    except requests.exceptions.RequestException as e:
        results.log_fail("Get ideas endpoint connection", str(e))
    
    return results.summary()

def test_get_random_idea():
    """Test GET /api/ideas/random endpoint"""
    print("\n🔍 Testing Get Random Idea Endpoint...")
    results = TestResults()
    
    try:
        # Test multiple times to ensure randomness works
        responses = []
        for i in range(3):
            response = requests.get(f"{API_BASE}/ideas/random", timeout=10)
            
            if response.status_code == 200:
                results.log_pass(f"Random idea endpoint returns 200 (attempt {i+1})")
                try:
                    data = response.json()
                    responses.append(data)
                    
                    # Test structure
                    required_fields = ["id", "text", "created_at", "user_submitted"]
                    for field in required_fields:
                        if field in data:
                            if i == 0:  # Only log once
                                results.log_pass(f"Random idea contains '{field}'")
                        else:
                            results.log_fail(f"Random idea missing field", f"Missing '{field}'")
                    
                except json.JSONDecodeError:
                    results.log_fail(f"Random idea response format (attempt {i+1})", "Invalid JSON response")
            else:
                results.log_fail(f"Random idea status code (attempt {i+1})", f"Expected 200, got {response.status_code}")
        
        # Test that we get different ideas (randomness)
        if len(responses) >= 2:
            texts = [r.get("text", "") for r in responses]
            if len(set(texts)) > 1:
                results.log_pass("Random endpoint returns different ideas")
            else:
                # This might be okay if we only have a few ideas, so just note it
                print(f"ℹ️  NOTE: All random requests returned same idea (might be expected with few ideas)")
                
    except requests.exceptions.RequestException as e:
        results.log_fail("Random idea endpoint connection", str(e))
    
    return results.summary()

def test_create_idea():
    """Test POST /api/ideas endpoint"""
    print("\n🔍 Testing Create Idea Endpoint...")
    results = TestResults()
    
    try:
        # Test creating a new idea
        payload = {"text": TEST_IDEA}
        response = requests.post(f"{API_BASE}/ideas", json=payload, timeout=10)
        
        if response.status_code == 200:
            results.log_pass("Create idea endpoint returns 200")
            
            try:
                data = response.json()
                
                # Test response structure
                required_fields = ["id", "text", "created_at", "user_submitted"]
                for field in required_fields:
                    if field in data:
                        results.log_pass(f"Created idea contains '{field}'")
                    else:
                        results.log_fail(f"Created idea missing field", f"Missing '{field}'")
                
                # Test values
                if data.get("text") == TEST_IDEA:
                    results.log_pass("Created idea text matches input")
                else:
                    results.log_fail("Created idea text", f"Expected '{TEST_IDEA}', got '{data.get('text')}'")
                
                if data.get("user_submitted") == True:
                    results.log_pass("Created idea marked as user_submitted")
                else:
                    results.log_fail("Created idea user_submitted", f"Expected True, got {data.get('user_submitted')}")
                
                # Test UUID format
                idea_id = data.get("id", "")
                if len(idea_id) == 36 and idea_id.count("-") == 4:
                    results.log_pass("Created idea has valid UUID format")
                else:
                    results.log_fail("Created idea ID format", f"Invalid UUID format: {idea_id}")
                    
            except json.JSONDecodeError:
                results.log_fail("Create idea response format", "Invalid JSON response")
                
        else:
            results.log_fail("Create idea status code", f"Expected 200, got {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error response: {error_data}")
            except:
                print(f"Error response body: {response.text}")
                
    except requests.exceptions.RequestException as e:
        results.log_fail("Create idea endpoint connection", str(e))
    
    return results.summary()

def test_duplicate_idea_error():
    """Test POST /api/ideas with duplicate idea (should return 409)"""
    print("\n🔍 Testing Duplicate Idea Error Handling...")
    results = TestResults()
    
    try:
        # Try to create a duplicate idea (should exist in default ideas)
        payload = {"text": DUPLICATE_IDEA}
        response = requests.post(f"{API_BASE}/ideas", json=payload, timeout=10)
        
        if response.status_code == 409:
            results.log_pass("Duplicate idea returns 409 Conflict")
            
            try:
                data = response.json()
                if "detail" in data and "already exists" in data["detail"].lower():
                    results.log_pass("Duplicate idea error message is appropriate")
                else:
                    results.log_fail("Duplicate idea error message", f"Unexpected error message: {data}")
                    
            except json.JSONDecodeError:
                results.log_fail("Duplicate idea error response format", "Invalid JSON response")
                
        else:
            results.log_fail("Duplicate idea status code", f"Expected 409, got {response.status_code}")
            try:
                error_data = response.json()
                print(f"Unexpected response: {error_data}")
            except:
                print(f"Unexpected response body: {response.text}")
                
    except requests.exceptions.RequestException as e:
        results.log_fail("Duplicate idea endpoint connection", str(e))
    
    return results.summary()

def test_invalid_input():
    """Test POST /api/ideas with invalid input"""
    print("\n🔍 Testing Invalid Input Handling...")
    results = TestResults()
    
    # Test empty text
    try:
        payload = {"text": ""}
        response = requests.post(f"{API_BASE}/ideas", json=payload, timeout=10)
        
        if response.status_code == 422:
            results.log_pass("Empty text returns 422 Validation Error")
        else:
            results.log_fail("Empty text validation", f"Expected 422, got {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        results.log_fail("Empty text validation connection", str(e))
    
    # Test missing text field
    try:
        payload = {}
        response = requests.post(f"{API_BASE}/ideas", json=payload, timeout=10)
        
        if response.status_code == 422:
            results.log_pass("Missing text field returns 422 Validation Error")
        else:
            results.log_fail("Missing text validation", f"Expected 422, got {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        results.log_fail("Missing text validation connection", str(e))
    
    # Test text too long (over 200 characters)
    try:
        long_text = "A" * 201  # 201 characters
        payload = {"text": long_text}
        response = requests.post(f"{API_BASE}/ideas", json=payload, timeout=10)
        
        if response.status_code == 422:
            results.log_pass("Text too long returns 422 Validation Error")
        else:
            results.log_fail("Text length validation", f"Expected 422, got {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        results.log_fail("Text length validation connection", str(e))
    
    return results.summary()

def run_all_tests():
    """Run all backend API tests"""
    print("🚀 Starting EmalfDraw Backend API Tests")
    print(f"Backend URL: {API_BASE}")
    print("="*60)
    
    all_passed = True
    
    # Test in logical order
    tests = [
        ("Health Check", test_health_endpoint),
        ("Get All Ideas", test_get_all_ideas),
        ("Get Random Idea", test_get_random_idea),
        ("Create New Idea", test_create_idea),
        ("Duplicate Idea Error", test_duplicate_idea_error),
        ("Invalid Input Handling", test_invalid_input)
    ]
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            passed = test_func()
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"❌ CRITICAL ERROR in {test_name}: {e}")
            all_passed = False
    
    print(f"\n🏁 ALL TESTS COMPLETED")
    if all_passed:
        print("🎉 ALL BACKEND TESTS PASSED!")
    else:
        print("⚠️  SOME BACKEND TESTS FAILED - See details above")
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)